#ifndef SAMPLE_H
#define SAMPLE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/*
 * Computes a + b with signed 32-bit overflow checking.
 * Returns true and stores the sum in *out on success.
 * Returns false without modifying *out on NULL pointer or overflow.
 */
bool sample_safe_add(int32_t a, int32_t b, int32_t *out);

/*
 * Sums count elements from values with signed 64-bit overflow checking.
 * If count == 0, stores 0 in *out and returns true (even if values == NULL).
 * Returns false on NULL out pointer, NULL values with count > 0, or overflow.
 */
bool sample_sum_array(const int32_t *values, size_t count, int64_t *out);

#endif /* SAMPLE_H */
