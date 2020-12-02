export tmp_setup_file_name=setup.tmp

[ -z $1 ] && echo "Package version is not provided!" && exit 1
[ -z $PYPI_PASSWORD ] && echo "Env variable PYPI_PASSWORD is not set!" && exit 1

echo 'Setting up package version...'

export VERSION=$1
mv setup.py $tmp_setup_file_name
envsubst < $tmp_setup_file_name > setup.py

echo 'Removing old dist files...'

rm -rf dist

echo 'Building a new dist file...'

python setup.py sdist

echo 'Uploading a new dist file...'

export TWINE_PASSWORD=$PYPI_PASSWORD
twine upload dist/*

mv $tmp_setup_file_name setup.py
