import csv, re, cStringIO, codecs

from pattern.web import abs, URL, DOM, plaintext, strip_between
from pattern.web import NODE, TEXT, COMMENT, ELEMENT, DOCUMENT

#unicode writer
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# Creating the csv output file for writing into as well as defining the writer
output = open("restweek.csv", "wb")
writer = UnicodeWriter(output)

# add header row
writer.writerow(["Name", "Neighborhood", "Cuisine", "Dining Style", "Meals Served", "Dress Code", "Ratings", "Price", "Phone Number", "Address", "Website" ])


# Get the DOM object to scrape for movie links. [Hint: Use absolute URL's.
# Documentation can be found here: http://www.clips.ua.ac.be/pages/pattern-web] 
url = URL("http://www.opentable.com/promo.aspx?m=7&ref=470&pid=90")
dom = DOM(url.download(cached=True))

for restaraunt in dom.by_class("ResultRow"):
    name = restaraunt.by_class("ReCol")[0].by_class("rinfo")[0].by_tag("a")[0].content.encode( 'ascii', 'ignore' )
    neighborhood_cuisine = restaraunt.by_class("ReCol")[0].by_class("rinfo")[0].by_class("d")[0].content.encode( 'ascii', 'ignore' )
    neihgborhood_cuisine =  neighborhood_cuisine.split('|')
    neighborhood = neihgborhood_cuisine[0]
    cuisine = neihgborhood_cuisine[1]
    meals = restaraunt.by_class("ReCol")[0].by_class("rinfo")[0].by_class("message")[0].content.encode( 'ascii', 'ignore' )
    meals = meals.split('<')
    # need to clean
    meals = meals[0]   
    restURL = URL(abs(restaraunt.by_class("ReCol")[0].by_class("rinfo")[0].by_tag("a")[0].attributes.get('href',''), base=url.redirect or url.string))
    restDOM = DOM(restURL.download(cached=True))
    # need to clean
    address = restDOM.by_id("ProfileOverview_lblAddressText").content
    price = restDOM.by_id("ProfileOverview_lblPriceText").content
    try:
        ratings = restDOM.by_id("RestPopLabel_ReviewsFormat")[0].attributes
        ratings = ratings['title']
    except TypeError:
        ratings = 'not available'
    style = restDOM.by_id("ProfileOverview_DiningStyle").by_class("value")[0].content
    try:
        website = restDOM.by_id("ProfileOverview_Website").by_tag("a")[0].content
    except AttributeError:
        website = "not available"
    phone = restDOM.by_id("ProfileOverview_Phone").by_class("value")[0].content
    dress = restDOM.by_id("ProfileOverview_DressCode").by_class("value")[0].content
    writer.writerow([name, neighborhood, cuisine, style, meals, dress, ratings, price, phone, address, website])

output.close()


