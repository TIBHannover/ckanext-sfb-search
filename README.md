 # ckanext-sfb-search-extension

Extending ckan search to search inside the csv/xlsx data resources in ckan. Besides, it creates tags for a dataset automatically based 
on the csv/xlsx columns' titles. 


## Requirements


Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8 and earlier | not tested    |
| 2.9             | Yes    |



## Installation

To install ckanext-sfb-search-extension:

1. Activate your CKAN virtual environment, for example:

        . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

        git clone https://git.tib.eu/lab-linked-scientific-knowledge/sfb-inf/ckanext-sfb-search-extension.git
        cd ckanext-sfb-search-extension
        pip install -e .
        pip install -r requirements.txt

3. Add `sfb_search` and `auto_tag` to the `ckan.plugins` setting in your CKAN config file (by default the config file is located at
    `/etc/ckan/default/ckan.ini`).

4. Run migration:

        ckan db upgrade -p sfb_search

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

        sudo service nginx reload




## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini



## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
