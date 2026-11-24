#include "sample.h"

#include <stdint.h>

bool sample_safe_add(int32_t a, int32_t b, int32_t *out) {
    if (out == NULL) {
        return false;
    }

    if (b > 0 && a > INT32_MAX - b) {
        return false;
    }
    if (b < 0 && a < INT32_MIN - b) {
        return false;
    }

    *out = a + b;
    return true;
}

bool sample_sum_array(const int32_t *values, size_t count, int64_t *out) {
    if (out == NULL) {
        return false;
    }
    if (count > 0 && values == NULL) {
        return false;
    }

    int64_t total = 0;
    for (size_t i = 0; i < count; ++i) {
        int64_t val = (int64_t)values[i];
        if (val > 0 && total > INT64_MAX - val) {
            return false;
        }
        if (val < 0 && total < INT64_MIN - val) {
            return false;
        }
        total += val;
    }

    *out = total;
    return true;
}
