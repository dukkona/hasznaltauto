# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
#scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".

from lxml import html
from lxml.etree import tostring
import requests
from BeautifulSoup import BeautifulSoup
import re
import scraperwiki


#brand = "volkswagen"
#model = "MUFT5FYQ6QOR9FZQ6FSHWPZFSK600O9QY21UYHJQSK6R2ESPZ66SKRCFWYZKHIZLE44URK3K4MKIYZICE9OHZQJSYPTR8EMZIQE0TWRZWRT2JGSY4W4HJIQCQG3GLH4QQYJ3OEWTZJOPIZGQ6LWT6CC6OHRCEECWLZ2EE/"
#model = "golf"

header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
#url_base = "http://www.hasznaltauto.hu/auto/" + brand + "/" + model + "/"
#url_base = "http://www.hasznaltauto.hu/talalatilista/auto/"  + model
url_base = "http://www.hasznaltauto.hu/talalatilista/auto/MUFT5FYQ6QOR9FZQ6FSHWPZFSK600O9QY21UYHJQSK6R2ESPZ66SKRCFWYZKHIZLE44URK3K4MKIYZICE9OHZQJSYPTR8EMZIQE0TWRZWRT2JGSY4W4HJIQCQG3GLH4QQYJ3OEWTZJOPIZGQ6LWT6CC6OHRCEECWLZ2EE/"
url_base_page = url_base + 'page1'

page = requests.get(url_base_page, headers=header)
tree = html.fromstring(page.content)

num_of_pages = int(tree.xpath('//*[@class="oldalszam"][last()]')[0].text)


database = []
age = []
cost = []

for i in range(num_of_pages):
    print i + 1, "/", num_of_pages

    url = url_base + "page" + str(i+1)
    page = requests.get(url, headers=header)
    tree = html.fromstring(page.content)

    links = tree.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " talalati_lista_head ")]')
    prices = tree.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " arsor ")]')
    years = tree.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " talalati_lista_infosor ")]')
    felszereltseg = tree.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " felszereltseg-nyomtatas ")]')
    kilometers = tree.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " talalati_lista_infosor ")]')

    for idx, price in enumerate(prices):
        try:
            price_string = price[0].text[:-3]
        except IndexError:
            #print "Ar nelkul"
            continue
        try:
            act_price = int(re.sub("\.", '', price_string))
        except ValueError:
            #print "Akcios"
            continue
        
        soup = BeautifulSoup(tostring(links[idx]))
        act_link = soup.find('a').get('href')

        try:
            soup = BeautifulSoup(tostring(years[idx]))
            text = soup.text
            pattern = "(\d{4}|\d{4}\/\d*)&#160;"
            act_year = re.findall(pattern, soup.text)
            
            if len(act_year) == 0:
                act_year = '0'
            else:
                act_year = act_year[0]

            if ';D&#237;zel' in text:
                act_motor = 'Diesel'
            elif 'Benzin' in text:
                act_motor = 'Benzin'
            else:
                act_motor = 'nincs adat'

            pattern_kobcenti = '(\d{4}) cm&#179;'
            act_kobcenti = re.findall(pattern_kobcenti, soup.text)

            if len(act_kobcenti) == 0:
                act_kobcenti = '0'
            else:
                act_kobcenti = act_kobcenti[0]

            pattern_loero = '(\d{2,3}&#160;LE)'
            loero_tmp = re.findall(pattern_loero, soup.text)[0]

            if len(loero_tmp) == 0:
                act_loero = '0'
            else:
                act_loero = loero_tmp.replace('&#160;LE', '')


        except IndexError:
            act_year = '0'
            act_loero = '0'
            act_kobcenti = '0'
            act_motor = 'nincs adat'

        try:
            soup = BeautifulSoup(tostring(felszereltseg[idx]))
            act_felszereltseg = soup.text[19:]
        except IndexError:
            act_felszereltseg = ''

        try:
            soup = BeautifulSoup(tostring(kilometers[idx]))
            act_kilometer = soup.find('abbr').string.replace('&#160;km', '')
        except IndexError:
            act_kilometer = '0'

        data = {
        'link': act_link, 
        'year': act_year, 
        'price': act_price, 
        'kilometer': act_kilometer, 
        'felszereltseg': act_felszereltseg,
        'motor': act_motor,
        'kobcenti': act_kobcenti,
        'loero: ': act_loero
        }
        #print(act_link, act_year, act_price, act_kilometer, act_felszereltseg, act_motor, act_kobcenti, act_loero)
        scraperwiki.sqlite.save(unique_keys=['link'], data=data)
