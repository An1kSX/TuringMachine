ifeq ($(OS),Windows_NT)
    LIB_NAME := tm_native.dll
    CXX := cl
    CXXFLAGS := /std:c++11 /O2 /LD
    LDFLAGS :=
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        LIB_NAME := libtm_native.dylib
        CXX := g++
        CXXFLAGS := -std=c++11 -O2 -fPIC
        LDFLAGS := -shared -static-libstdc++ -Wl,-install_name,@rpath/$(LIB_NAME)
    else
        LIB_NAME := libtm_native.so
        CXX := g++
        CXXFLAGS := -std=c++11 -O2 -fPIC
        LDFLAGS := -shared -static-libstdc++
    endif
endif

BUILD_DIR := _build
CPP_DIR   := cpp
SRCS      := $(wildcard $(CPP_DIR)/*.cpp)
TARGET    := $(BUILD_DIR)/$(LIB_NAME)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRCS) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $@ $(LDFLAGS)
	@echo "Built $(TARGET)"

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	-rm -f $(TARGET)
