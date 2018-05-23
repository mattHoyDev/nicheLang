cmake_minimum_required(VERSION 3.10)
project(niche_lang_cpp)

set(CMAKE_CXX_STANDARD 17)

add_executable(lexParse main.cpp Lexer.cpp Lexer.h common.h)
