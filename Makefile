PRODUCT: README.html

all: $(PRODUCT)
	
clean:
	rm -f $(PRODUCT)

README.md: litterate.py
	./litterate.py $< > $@

%.html: %.md
	pandoc $< -o $@ --css texto.css

