CC = gcc
CFLAGS = -fPIC -Wall -Wextra
LDFLAGS = -shared

SRCS = queue.c stack.c circular_list.c
OBJS = $(SRCS:.c=.o)
TARGET = libword_learning.so

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean 