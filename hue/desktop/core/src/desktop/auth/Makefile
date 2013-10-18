CC := gcc
CFLAGS := -Wall -lpam
DESTDIR := build

default:
#default: $(DESTDIR)/pam_auth

$(DESTDIR)/pam_auth: pam_auth.c
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@
	chmod 4711 $@

clean:
	rm -rf $(DESTDIR)
