/**
 * Convert ASTM standard grain size to an quivalent diameter in mm
 * @param {number} value
 */
export const ASTM2Dia = astm => Math.round((0.25 / Math.sqrt(2.0 ** (astm - 1.0))) * 100) / 100

/**
 * Convert grain diameter in mm to ASTM standard grain size
 * @param {number} dia
 */
export const dia2ASTM = dia => Math.round((Math.log((0.25 / dia) ** 2) / Math.log(2.0)) * 100) / 100
