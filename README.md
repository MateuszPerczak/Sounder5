# Sounder5

## Music player written in python

Note: Sounder is still in development. Please keep in mind that the final appearance may change!

#

<p align="center"><img src="images/app.png" alt="Sounder"></p>

## Running app in container

In docker-compose:

```sh
docker-compose up
```

In docker:

```sh
docker build . -t sounder
docker run sounder
```

In podman:

```sh
podman build . -t sounder
podman run sounder
```

In podman on wsl:

```sh
podman build . -t sounder --events-backend=file
podman run sounder --events-backend=file
```

In docker for development purpose:

```sh
docker build . -t sounder-dev -f Dockerfile.dev
docker run -it sounder-dev
```

## Used Libraries

- tkinter
- os
- json
- logging
- traceback
- PIL
- io
- random
- string
- requests
- threading
- mutagen
- win10toast (modified)
- psutil
- zipfile
- hashlib
- difflib
- ctypes
- 

### Sounder logo

Logo designer: [reallinfo](https://github.com/reallinfo)

### Sounder icons

Icons: [icons8](https://icons8.com/)


<p align="center"><img src="images/horizontal.png" alt="Sounder" height="120px"></p>

