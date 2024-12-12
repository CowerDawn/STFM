TARGET = stfm
SRC = STFM.c
CFLAGS = -Wall -Wextra -O2
LDFLAGS = -lncurses

ifeq ($(shell command -v apt-get 2>/dev/null),)
    ifeq ($(shell command -v yum 2>/dev/null),)
        ifeq ($(shell command -v dnf 2>/dev/null),)
            ifeq ($(shell command -v pacman 2>/dev/null),)
                $(error "No supported package manager found (apt-get, yum, dnf, pacman)")
            else
                PKG_MANAGER = pacman
                PKG_INSTALL = sudo pacman -S --noconfirm
                DEPENDENCIES = ncurses
            endif
        else
            PKG_MANAGER = dnf
            PKG_INSTALL = sudo dnf install -y
            DEPENDENCIES = ncurses-devel
        endif
    else
        PKG_MANAGER = yum
        PKG_INSTALL = sudo yum install -y
        DEPENDENCIES = ncurses-devel
    endif
else
    PKG_MANAGER = apt-get
    PKG_INSTALL = sudo apt-get install -y
    DEPENDENCIES = libncurses-dev
endif

install:
	$(PKG_INSTALL) $(DEPENDENCIES)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET)

all: install $(TARGET)

distclean: clean
	rm -f $(TARGET)

.PHONY: all install clean distclean
