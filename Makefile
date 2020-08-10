# Makefile for stm32-j1708

###############################################################################

PROGRAM  = stm32-j1708
CROSS   ?= arm-none-eabi-
OBJS     = $(patsubst %.c,%.o,$(wildcard *.c))
DEPS     = $(patsubst %.c,%.d,$(wildcard *.c))

###############################################################################

CC       = $(CROSS)gcc
LD       = $(CROSS)ld
OBJCOPY  = $(CROSS)objcopy
OBJDUMP  = $(CROSS)objdump
SIZE     = $(CROSS)size
NM       = $(CROSS)nm

ELF      = $(PROGRAM).elf
BIN      = $(PROGRAM).bin
HEX      = $(PROGRAM).hex
MAP      = $(PROGRAM).map
DMP      = $(PROGRAM).out

# Board-specific defs
ARCH_FLAGS = -DSTM32F1 -mthumb -mcpu=cortex-m3 -msoft-float -mfix-cortex-m3-ldrd
LDSCRIPT   = libopencm3/lib/stm32/f1/stm32f103x8.ld
LIBOPENCM3 = libopencm3/lib/libopencm3_stm32f1.a
OPENCM3_MK = lib/stm32/f1

# C options
CFLAGS  += -O3 -std=gnu99 \
			-Wall -Wextra -Wimplicit-function-declaration \
			-Wredundant-decls -Wmissing-prototypes -Wstrict-prototypes \
			-Wundef -Wshadow -fno-common -Wstrict-prototypes \
			-ffunction-sections -fdata-sections -MD
CFLAGS  += $(ARCH_FLAGS) -Ilibopencm3/include/

LIBC     = $(shell $(CC) $(CFLAGS) --print-file-name=libc.a)
LIBGCC   = $(shell $(CC) $(CFLAGS) --print-libgcc-file-name)

# LDPATH is required for libopencm3 ld scripts to work.
LDPATH   = libopencm3/lib/
#LDFLAGS += -L$(LDPATH) -T$(LDSCRIPT) -Map $(MAP) --gc-sections --print-gc-sections
LDFLAGS += -L$(LDPATH) -T$(LDSCRIPT) -Map $(MAP) --gc-sections
LDLIBS  += $(LIBOPENCM3) $(LIBC) $(LIBGCC)

.PHONY: firmware clean distclean flash size symbols

firmware: $(BIN) $(HEX) $(DMP) size

$(ELF): $(LDSCRIPT) $(OBJS) $(LIBOPENCM3)
	$(LD) -o $@ $(LDFLAGS) $(OBJS) $(LDLIBS)

$(DMP): $(ELF)
	$(OBJDUMP) -d $< > $@

%.hex: %.elf
	$(OBJCOPY) -S -O ihex   $< $@

%.bin: %.elf
	$(OBJCOPY) -S -O binary $< $@

%.o: %.c $(LIBOPENCM3)
	$(CC) $(CFLAGS) -c $< -o $@

%.html: %.md
	markdown $< > $@

$(LIBOPENCM3):
	git submodule init
	git submodule update --init
	CFLAGS="$(CFLAGS)" $(MAKE) -C libopencm3 $(OPENCM3_MK) PREFIX=$(patsubst %,%,$(CROSS)) V=1

flashrom/flashrom:
	git submodule init
	git submodule update --init
	$(MAKE) -C flashrom

clean:
	rm -f $(OBJS) $(DEPS) $(DOCS) $(ELF) $(HEX) $(BIN) $(MAP) $(DMP)

distclean: clean
	$(MAKE) -C libopencm3 clean
	rm -f *~ *.swp *.hex *.bin

flash: $(HEX)
	st-flash --reset --format ihex write $<

size: $(PROGRAM).elf
	@echo ""
	@$(SIZE) $(PROGRAM).elf
	@echo ""

symbols: $(ELF)
	@$(NM) --demangle --size-sort -S $< | grep -v ' [bB] '

