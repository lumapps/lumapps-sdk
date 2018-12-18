
make clean
make html
cd ..
rm -rf out
git clone git@github.com:lumapps/lumapps-sdk.git out
cd out
git checkout gh-pages || git checkout --orphan gh-pages
git rm -rf .
cd ..

cp -a documentation/build/html/* out/

cd out
git add -A
git commit -m "Automated deployement to Github Page"

git push origin gh-pages