cmake_minimum_required(VERSION 3.10)
project(niche_lang)

set(CMAKE_CXX_STANDARD 17)

add_executable(tokenizer tokenizer.cpp)
add_executable(tokenizerc tokenizer.c)
