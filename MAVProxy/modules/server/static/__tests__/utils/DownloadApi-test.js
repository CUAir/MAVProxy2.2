import { saveParamsToFile, saveFenceToFile } from 'js/utils/DownloadApi';

describe('DownloadApi', function() {

  describe('saveParamsToFile', function() {
    const params = [{
      name: 'P1', value: 0, description: 'desc', documentation: 'doc', key: 'P1'
    }, {
      name: 'P2', value: 1, description: 'ript', documentation: 'ument', key: 'P2'
    }, {
      name: 'P3', description: 'ion', documentation: 'ation', key: 'P3'
    }];
    it('downloads correct string', function() {
      const fileContents = saveParamsToFile('input', params);
      expect(fileContents.includes('#Note: '));
      expect(fileContents.includes('input')).toEqual(true);
      expect(fileContents.includes('P1,0')).toEqual(true);
      expect(fileContents.includes('P2,1')).toEqual(true);
      expect(fileContents.includes('P3')).toEqual(false);
    });
  });

  describe('saveFenceToFile', function() {
    const fence = [{
      lat: 5, lon: 10
    }, {
      lat: 6, lon: 11
    }, {
      lat: 7, lon: 12
    }];
    it('downloads correct string', function() {
      const fileContents = saveFenceToFile(fence);
      expect(fileContents.includes('5 10'));
      expect(fileContents.includes('6 11'));
      expect(fileContents.includes('7 12'));
    });
  });
});
