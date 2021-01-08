
.PHONY: firmware clean distclean flash

build:
	make -C firmware/ $@

clean:
	make -C firmware/ $@

distclean:
	make -C firmware/ $@

flash:
	make -C firmware/ $@
