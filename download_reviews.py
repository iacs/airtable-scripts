import os
import re
import unicodedata
import datetime
import airtable
from dotenv import load_dotenv


def main():
    load_dotenv()
    apikey = os.getenv('AIRTABLE_API_KEY')
    baseid = os.getenv('BASE_ID')
    atb = airtable.Airtable(apikey, baseid)
    reviews = get_reviews(atb)
    result = save_files(reviews)
    update_table(atb, reviews)


def get_reviews(atb):
    params = {'filterByFormula': 'Status="Reviewed"'}
    data = atb.get_table('Films', params)
    try:
        films = data.get('records')
        return films
    except KeyError as err:
        print('No key!!', err)


def save_files(reviews):
    for film in reviews:
        filename = _slugify(film.get('fields').get('Title'))
        filename += '.md'
        frontmatter = dict_to_frontmatter(film.get('fields'))
        review = film.get('fields').get('Review', "WRITE REVIEW HERE")
        if filename and frontmatter and review:
            write_file(filename, frontmatter, review)


def dict_to_frontmatter(data):
    table_to_matter = {
        'Title': 'title',
        'Originaltitle': 'orig_title',
        'seen_year': 'seen_year',
        'seen_month': 'seen_month',
        'Year': 'year',
        'Director': 'director',
        'Genre': 'genre',
        'Stars': 'stars',
    }
    mapped = dict()
    for key, value in data.items():
        try:
            mapped[table_to_matter[key]] = value
        except KeyError as err:
            print(f"  =* [{data['Title']}] Not matching {err}")
    try:
        result = '---\n'
        for key, value in mapped.items():
            if key == 'title' or key == 'orig_title':
                result += f'{key}: "{value}"\n'
            elif key == 'director':
                directors = ", ".join(value)
                result += f'{key}: "{directors}"\n'
            else:
                result += f'{key}: {value}\n'
        result += 'still: ../stills/\n'
        result += '---\n'
        return result
    except KeyError as err:
        print('key not found. Aborting')
        print(data, err)
        return None


def write_file(filename, fmt, review):
    filepath = f'reviews/{filename}'
    with open(filepath, 'w') as revfile:
        revfile.write(fmt)
        revfile.write(review)
    print(f'== Wrote file at {filepath}')


def update_table(atb, data):
    to_update = list()
    for item in data:
        entry = {
            'id': item['id'],
            'fields': {
                'Status': 'Extracted',
                'Extractiondate': str(datetime.date.today())
            }
        }
        to_update.append(entry)
    # Airtable has a limit of <max_records> per update
    max_records = 10
    request_chunks = [to_update[i:i+max_records] for i in range(0, len(to_update), max_records)]
    for chunk in request_chunks:
        payload = {'records': chunk}
        atb.patch_table('Films', payload)


def _slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('-_')


if __name__ == "__main__":
    main()
