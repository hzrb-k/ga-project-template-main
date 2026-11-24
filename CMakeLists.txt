cmake_minimum_required(VERSION 3.16)

project(c_project_template
    VERSION 0.1.0
    LANGUAGES C
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(ENABLE_SANITIZERS "Enable AddressSanitizer/UndefinedBehaviorSanitizer in Debug builds when supported" ON)

include(CheckCSourceCompiles)
include(CTest)

add_library(project_options INTERFACE)

if(MSVC)
    target_compile_options(project_options INTERFACE /W4 /WX)
elseif(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang|AppleClang")
    target_compile_options(project_options INTERFACE -Wall -Wextra -Werror)
endif()

if(ENABLE_SANITIZERS)
    if(MSVC)
        set(_orig_c_flags_debug "${CMAKE_C_FLAGS_DEBUG}")
        # MSVC /fsanitize=address is incompatible with /RTC1 in Debug flags.
        string(REGEX REPLACE "/RTC(su|[1su])" "" CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG}")

        set(CMAKE_REQUIRED_FLAGS "/fsanitize=address")
        check_c_source_compiles("int main(void) { return 0; }\n" HAVE_MSVC_ASAN)
        unset(CMAKE_REQUIRED_FLAGS)

        if(HAVE_MSVC_ASAN)
            target_compile_options(project_options INTERFACE $<$<CONFIG:Debug>:/fsanitize=address>)
            target_link_options(project_options INTERFACE $<$<CONFIG:Debug>:/INCREMENTAL:NO>)
            message(STATUS "ENABLE_SANITIZERS: MSVC AddressSanitizer enabled for Debug (UBSan is unavailable on MSVC).")
        else()
            set(CMAKE_C_FLAGS_DEBUG "${_orig_c_flags_debug}")
            message(WARNING "ENABLE_SANITIZERS: MSVC AddressSanitizer is not supported by this toolchain; disabled.")
        endif()
        unset(_orig_c_flags_debug)
    elseif(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang|AppleClang")
        set(CMAKE_REQUIRED_FLAGS "-fsanitize=address,undefined -fno-omit-frame-pointer")
        set(CMAKE_REQUIRED_LINK_OPTIONS "-fsanitize=address,undefined")
        check_c_source_compiles("int main(void) { return 0; }\n" HAVE_ASAN_UBSAN)
        unset(CMAKE_REQUIRED_FLAGS)
        unset(CMAKE_REQUIRED_LINK_OPTIONS)

        if(HAVE_ASAN_UBSAN)
            target_compile_options(project_options INTERFACE
                $<$<CONFIG:Debug>:-fsanitize=address,undefined;-fno-omit-frame-pointer>
            )
            target_link_options(project_options INTERFACE
                $<$<CONFIG:Debug>:-fsanitize=address,undefined>
            )
            message(STATUS "ENABLE_SANITIZERS: ASan and UBSan enabled for Debug builds.")
        else()
            message(WARNING "ENABLE_SANITIZERS: -fsanitize=address,undefined is not supported by this compiler/linker; disabled.")
        endif()
    else()
        message(WARNING "ENABLE_SANITIZERS: Unsupported compiler '${CMAKE_C_COMPILER_ID}'; disabled.")
    endif()
endif()

add_library(app_core STATIC
    src/sample.c
)

target_include_directories(app_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(app_core
    PRIVATE
        project_options
)

if(BUILD_TESTING)
    add_executable(test_sample
        tests/test_sample.c
    )

    target_link_libraries(test_sample
        PRIVATE
            app_core
            project_options
    )

    add_test(NAME UT_SAMPLE COMMAND test_sample)
    set_tests_properties(UT_SAMPLE PROPERTIES TIMEOUT 10)
endif()
