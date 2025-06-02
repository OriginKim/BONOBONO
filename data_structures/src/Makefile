CC = gcc
CFLAGS = -fPIC -Wall -Wextra -fvisibility=default
LDFLAGS = -shared

SRCS = stack.c queue.c circular_list.c
OBJS = $(SRCS:.c=.o)
TARGET = libword.so

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean 