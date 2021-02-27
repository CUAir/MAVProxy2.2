// @flow

/**
 * @module constants/Frequency
 */

/** How many times per second to retrieve plane vitals
 * some of the less critical information will be updated at half this speed
 * @type {number}
 */
export const PLANE_RECEIVE_FREQUENCY = 1;


/** How many times per second to retrieve interop data
 * @type {number}
 */
export const INTEROP_RECEIVE_FREQUENCY = 5;

export const EPSILON = 0.0001;

