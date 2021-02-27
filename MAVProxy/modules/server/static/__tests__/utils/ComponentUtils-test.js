jest.mock('js/utils/MapUtils');

import { enabledToSuccess, colorToButton, valueToPercent, valueToColor,
         decround, pythagorean } from 'js/utils/ComponentUtils';

describe('ComponentUtils', function () {
  describe('enabledToSuccess', function() {
    it('returns success if enabled', function() {
      expect(enabledToSuccess(true)).toEqual('success');
    });

    it('returns error if not enabled', function() {
      expect(enabledToSuccess(false)).toEqual('error');
    });
  });

  describe('colorToButton', function() {
    it('returns correct values', function() {
      expect(colorToButton('success')).toEqual('btn-success');
      expect(colorToButton('error')).toEqual('btn-danger');
      expect(colorToButton('warning')).toEqual('btn-warning');
    });

    it('returns correct default value', function() {
      expect(colorToButton('random')).toEqual('btn-primary');
    });
  });

  describe('valueToPercent', function() {
    it('handles integers correctly', function() {
      expect(valueToPercent(25)).toEqual(': 25%');
    });

    it('handles floats correctly', function() {
      expect(valueToPercent(12.2)).toEqual(': 12%');
    });

    it('handles negatives correctly', function() {
      expect(valueToPercent(-5)).toEqual(': -5%');
    });
  });

  describe('valueToColor', function() {
    it('handles regular numbers correctly', function() {
      expect(valueToColor(25)).toEqual('error');
      expect(valueToColor(50)).toEqual('warning');
      expect(valueToColor(80)).toEqual('success');
    });

    it('handles negatives correctly', function() {
      expect(valueToColor(-5)).toEqual('error');
    });

    it('handles greater than 100 values correctly', function() {
      expect(valueToColor(120)).toEqual('success');
    });
  });

  describe('decround', function() {
    it('handles regular values correctly', function() {
      expect(decround(15.234, 2)).toEqual(15.23);
      expect(decround(15.237, 2)).toEqual(15.24);
      expect(decround(15.2, 2)).toEqual(15.2);
    });

    it('handles 0 case correctly', function() {
      expect(decround(15.67, 0)).toEqual(16);
    });

    it('handles negatives correctly', function() {
      expect(decround(126.723, -2)).toEqual(100);
    });
  });

  describe('pythagorean', function() {
    it('correctly calculates pythagorean values', function() {
      expect(pythagorean(2, 3, 6)).toEqual(7);
    });

    it('handles negatives correctly', function() {
      expect(pythagorean(-2, 3, -6)).toEqual(7);
    });
  });
});
