# Building Packages

Released packages are [built and published via GitHub actions](maintainers.md#drafting-releases).

## Python packages

To build Python packages locally for testing, use [`task`](starting-dev-server.md#without-dev-containers). After installing `task`, run `task py:package` to perform all the steps needed to build the package and a requirements file. To do it manually, run:
```sh
pushd frontend
yarnpkg install
yarnpkg generate
popd
rm -r mealie/frontend
cp -a frontend/dist mealie/frontend
poetry build
poetry export -n --only=main --extras=pgsql --output=dist/requirements.txt
MEALIE_VERSION=$(poetry version --short)
echo "mealie[pgsql]==${MEALIE_VERSION} \\" >> dist/requirements.txt
poetry run pip hash dist/mealie-${MEALIE_VERSION}-py3-none-any.whl | tail -n1 | tr -d '\n' >> dist/requirements.txt
echo " \\" >> dist/requirements.txt
poetry run pip hash dist/mealie-${MEALIE_VERSION}.tar.gz | tail -n1 >> dist/requirements.txt
```

The Python package can be installed with all of its dependencies pinned to the versions tested by the developers with:
```sh
pip3 install -r dist/requirements.txt --find-links dist
```

To install with the latest but still compatible dependency versions, instead run `pip3 install dist/mealie-$VERSION-py3-none-any.whl` (where `$VERSION` is the version of mealie to install).

## Docker image
One way to build the Docker image is to run the following command in the project root directory:
```sh
docker build --tag mealie:dev --file docker/Dockerfile --build-arg COMMIT=$(git rev-parse HEAD) .
```

The Docker image can be built from the pre-built Python packages with the task command `task docker:build-from-package`. This is equivalent to:
```sh
docker build --tag mealie:dev --file docker/Dockerfile --build-arg COMMIT=$(git rev-parse HEAD) --build-context packages=dist .
```
