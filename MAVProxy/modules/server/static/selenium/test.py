import unittest
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

url = 'http://localhost:8001/static/gcs2/index.html'

def is_float(element, start=None, end=None):
  try:
    float(element.text[start:end])
    return True
  except ValueError:
    return False
  except NoSuchElementException:
    return False
  except Exception as e:
    print 'Unhandled Exception' + str(e)
    return False

class SimpleTests(unittest.TestCase):
  def setUp(self):
    self.driver = webdriver.Chrome()
    self.driver.set_window_size(1500, 800)

  def tearDown(self):
    self.driver.quit()

  def test_page(self):
    self.driver.get(url)
    self.assertEqual('CUAir Ground Station', self.driver.title)

  def test_plane_info_numbers(self):
    self.driver.get(url)
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="REL_ALT"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="GROUND_SPEED"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="AIR_SPEED"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="ROLL"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="PITCH"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="YAW"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="LATITUDE"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="LONGITUDE"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="WIND"]/td[2]/span[1]')))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="THROTTLE"]/td[2]/span[1]')))

  def test_plane_actions(self):
    self.driver.get('http://localhost:8001/static/gcs2/index.html')
    self.driver.find_element_by_xpath('//*[@id="MODE_SWITCH"]/td[2]/div/button/span[1]').click()
    self.driver.find_element_by_xpath('//*[@id="MODE_SWITCH"]/td[2]/div/ul/li[2]/a').click()
    self.driver.find_element_by_xpath('//*[@id="CURRENT_MODE"]/td[2]/div/button/span[1]').click()
    self.driver.find_element_by_xpath('//*[@id="CURRENT_MODE"]/td[2]/div/ul/li[3]/a').click()
    toggle_interop_before = self.driver.find_element_by_xpath('//*[@id="TOGGLE_INTEROP"]').get_attribute('class')
    interopOnBefore = 'btn-success' in toggle_interop_before
    time.sleep(4)
    toggle_interop_after = self.driver.find_element_by_xpath('//*[@id="TOGGLE_INTEROP"]').get_attribute('class')
    interopOnAfter = 'btn-success' in toggle_interop_after
    #self.assertNotEqual(interopOnBefore, interopOnAfter)
    self.assertEqual(self.driver.find_element_by_xpath('//*[@id="MODE_SWITCH"]/td[2]/div/button/span[1]').text,
      'AUTO')
    self.assertEqual(self.driver.find_element_by_xpath('//*[@id="CURRENT_MODE"]/td[2]/div/button/span[1]').text,
      'AUTOTUNE')
    self.driver.find_element_by_xpath('//*[@id="RETURN_HOME"]').click()
    time.sleep(3)
    self.assertEqual(self.driver.find_element_by_xpath('//*[@id="CURRENT_MODE"]/td[2]/div/button/span[1]').text,
      'RTL')

  def test_settings(self):
    self.driver.get(url)
    self.driver.find_element_by_xpath('//*[@id="navbar-collapse-1"]/ul[1]/li[2]').click()
    self.driver.find_element_by_xpath('//*[@id="LOCATION"]/td[2]/div/button').click()
    self.driver.find_element_by_xpath('//*[@id="LOCATION"]/td[2]/div/ul/li[2]/a').click()
    self.assertEqual(self.driver.find_element_by_xpath('//*[@id="LOCATION"]/td[2]/div/button').text,
      'PAX River AFB')
    self.assertEqual(self.driver.find_element_by_xpath('//*[@id="FENCES"]/td[2]/input').get_attribute('value'),
      'true')
    self.assertEqual(self.driver.find_element_by_xpath('//*[@id="OFFLINE"]/td[2]/input').get_attribute('value'),
      'false')

  def test_plane_state(self):
    self.driver.get(url)
    armed = self.driver.find_element_by_xpath('//*[@id="ARMED"]').get_attribute('class')
    self.assertTrue((armed == 'success') or (armed == 'error'))
    plane_link = self.driver.find_element_by_xpath('//*[@id="PLANE_LINK"]').get_attribute('class')
    self.assertTrue((plane_link == 'success') or (plane_link == 'error'))
    gps_link = self.driver.find_element_by_xpath('//*[@id="GPS_LINK"]').get_attribute('class')
    self.assertTrue((gps_link == 'success') or (gps_link == 'error'))
    self.assertTrue(is_float(self.driver.find_element_by_xpath('//*[@id="BATTERY"]/a/span[2]'), start=2, end=-1))

  def test_parameters(self):
    self.driver.get(url)
    self.driver.find_element_by_xpath('//*[@id="navbar-collapse-1"]/ul[1]/li[3]').click()
    self.driver.find_element_by_xpath('//*[@id="NOTE"]').send_keys('test note')
    time.sleep(0.1)
    self.assertEqual(self.driver.find_element_by_xpath('//*[@id="NOTE"]').get_attribute('value'), 'test note')
    self.driver.find_element_by_xpath('//*[@id="AFS_AMSL_ERR_GPS"]/td[3]/div/input').send_keys(Keys.BACK_SPACE * 2)
    self.driver.find_element_by_xpath('//*[@id="AFS_AMSL_ERR_GPS"]/td[3]/div/input').send_keys('5')
    self.driver.find_element_by_xpath('//*[@id="AFS_AMSL_ERR_GPS"]').click()
    self.driver.find_element_by_xpath('//*[@id="SEND_PARAM"]').click()
    self.driver.find_element_by_xpath('//*[@id="AHRS_EKF_USE"]/td[3]/div/button').click()
    self.driver.find_element_by_xpath('//*[@id="AHRS_EKF_USE"]/td[3]/div/ul/li[2]').click()
    self.driver.find_element_by_xpath('//*[@id="AHRS_TRIM_Z"]/td[3]/div/input').send_keys(Keys.BACK_SPACE)
    self.driver.find_element_by_xpath('//*[@id="AHRS_TRIM_Z"]/td[3]/div/input').send_keys('-2')
    time.sleep(5)
    self.assertEqual('', self.driver.find_element_by_xpath('//*[@id="AHRS_TRIM_Z"]/td[3]/div/input').get_attribute('value'))
    self.assertIn(' color: black;', self.driver.find_element_by_xpath('//*[@id="AFS_AMSL_ERR_GPS"]/td[3]/div/input').get_attribute('style'))
    self.assertEqual('5', self.driver.find_element_by_xpath('//*[@id="AFS_AMSL_ERR_GPS"]/td[3]/div/input').get_attribute('value'))
    self.assertEqual('Enabled', self.driver.find_element_by_xpath('//*[@id="AHRS_EKF_USE"]/td[3]/div/button/span[1]').text)

  def test_calibration(self):
    self.driver.get(url)
    self.driver.find_element_by_xpath('//*[@id="navbar-collapse-1"]/ul[1]/li[4]').click()
    self.driver.find_element_by_xpath('//*[@id="CALIBRATION_G_START"]').click()
    #self.assertLess(0, len(self.driver.find_element_by_xpath('//*[@id="calibration"]/div/div[1]').find_elements_by_xpath('/center')))
    self.driver.find_element_by_xpath('//*[@id="CALIBRATION_CLEAR"]').click()
    self.assertEqual(0, len(self.driver.find_element_by_xpath('//*[@id="calibration"]/div/div[1]').find_elements_by_xpath('/center')))

if __name__ == '__main__':
    unittest.main()