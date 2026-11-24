#include "sample.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

static int g_failures = 0;

#define CHECK(cond)                                                                                \
    do {                                                                                           \
        if (!(cond)) {                                                                             \
            (void)fprintf(stderr, "FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond);                 \
            g_failures++;                                                                          \
        }                                                                                          \
    } while (0)

static void test_ut_sample_001_safe_add_normal(void) {
    int32_t result = 0;
    CHECK(sample_safe_add(12, 30, &result));
    CHECK(result == 42);

    CHECK(sample_safe_add(-10, 4, &result));
    CHECK(result == -6);

    CHECK(sample_safe_add(10, -4, &result));
    CHECK(result == 6);

    CHECK(sample_safe_add(5, 0, &result));
    CHECK(result == 5);

    CHECK(sample_safe_add(0, INT32_MIN, &result));
    CHECK(result == INT32_MIN);
}

static void test_ut_sample_002_safe_add_overflow_and_null(void) {
    int32_t result = 123;
    CHECK(!sample_safe_add(INT32_MAX, 1, &result));
    CHECK(result == 123);

    CHECK(!sample_safe_add(INT32_MIN, -1, &result));
    CHECK(result == 123);

    CHECK(!sample_safe_add(-1, INT32_MIN, &result));
    CHECK(result == 123);

    CHECK(!sample_safe_add(1, 2, NULL));
}

static void test_ut_sample_003_sum_array_normal_and_boundary(void) {
    const int32_t values[] = {10, -3, 25, INT32_MAX};
    int64_t total = 0;
    CHECK(sample_sum_array(values, sizeof(values) / sizeof(values[0]), &total));
    CHECK(total == (int64_t)32 + (int64_t)INT32_MAX);

    CHECK(sample_sum_array(NULL, 0, &total));
    CHECK(total == 0);
}

static void test_ut_sample_004_sum_array_invalid_args(void) {
    int64_t total = 99;
    CHECK(!sample_sum_array(NULL, 3, &total));
    CHECK(total == 99);

    const int32_t values[] = {1};
    CHECK(!sample_sum_array(values, 1, NULL));
}

int main(void) {
    test_ut_sample_001_safe_add_normal();
    test_ut_sample_002_safe_add_overflow_and_null();
    test_ut_sample_003_sum_array_normal_and_boundary();
    test_ut_sample_004_sum_array_invalid_args();

    if (g_failures > 0) {
        (void)fprintf(stderr, "Total failures: %d\n", g_failures);
        return 1;
    }

    return 0;
}
