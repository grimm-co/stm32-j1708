
.PHONY: firmware clean distclean flash

build:
clean:
distclean:
flash:
	make -C firmware/ $@
