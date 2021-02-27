# GCS 3
The New CUAir GCS runs on React and Redux and is styled under material design.

## Contributing
To download the dependencies if you want to contribute, make sure you have npm then go to the repo's root directory and type `npm install`

To run the build after running npm install, go to the repo's root directory and type ` gulp `

## Running
To test offline open `index.html` in the root repository
To test online, check the [CUAir wiki](http://cuair.wikia.com/wiki/Autopilot)
and run MAVProxy then navigate to <http://localhost:8001/static/gcs2/index.html> in your browser

Make sure javascript is enabled in your browser or else it won't load

## Testing
Selenium testing is currently being added
To run the tests, make sure you're running the SITL and can access <http://localhost:8001/static/gcs2/index.html>

To install dependencies
If it's your first time running the tests do the following before running the tests (starting in the gcs root directory):
```
cd test
./setup.sh
```

To run the tests (starting in the gcs root directory):
```
cd test
source venv/bin/activate
python test.py
```

The tests currently take 30-60 seconds to run because it takes the backend some time to register changes to the SITL

## Browser Support
We strongly recommend using Chrome to use the Ground Station because it's what we use so it's the most tested, but Firefox and Safari seem to work pretty well too. We do not support any version of IE, nor are we planning on adding support any time soon.

Also, the app is responsive so it should behave nicely with phones and tablets ... you should probably use chrome if your mobile OS supports it.

## Todo
* Make sure DO_JUMP waypoints work
