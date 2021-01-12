
.PHONY: default clean flash

default:
	make -C firmware/ $@

clean:
	make -C firmware/ $@

flash:
	make -C firmware/ $@
