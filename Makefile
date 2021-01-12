
.PHONY: default flash clean distclean

default:
	make -C firmware/ $@

flash:
	make -C firmware/ $@

clean:
	make -C firmware/ $@

distclean:
	make -C firmware/ $@
