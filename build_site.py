#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Perth Adventure — single source of truth.
Generates:
  * print/perth_adventure_map.svg (+ .html)  — A2 printable map
  * index.html                               — interactive clickable map
  * js/data.js                               — place data for the detail pages
Run:  python3 build_site.py
"""
import math, json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================ PROJECTION
LON0    = 115.55
LAT_TOP = -31.45
COSLAT  = math.cos(math.radians(32.0))     # ~0.848
SCALE   = 420.0                             # mm per degree

# print-map layout (mm, A2 portrait)
W, H = 420.0, 594.0
MX0, MY0, MW, MH = 15.0, 66.0, 266.0, 508.0
PX0 = 288.0
PW  = W - PX0 - 8.0

def proj(lat, lon):
    x = MX0 + (lon - LON0) * COSLAT * SCALE
    y = MY0 + 4.0 + (LAT_TOP - lat) * SCALE
    return x, y

# ============================================================ COLOURS
COL = {
    "park":       "#2e8b57",
    "beach":      "#1f78b4",
    "attraction": "#e69500",
    "hills":      "#8B5A2B",
    "historic":   "#7b3fa0",
    "food":       "#c1121f",
    "suburb":     "#5f6b7a",
    "home":       "#e53935",
}
CAT_LABEL = {
    "park":"Parks & nature", "beach":"Beaches & water", "attraction":"Attractions",
    "hills":"Hills & towns", "historic":"Historic sites", "food":"Food, wine & brew",
    "suburb":"Suburbs & localities", "home":"Home",
}
OCEAN="#d7ecf6"; RIVER="#8fcfe8"; RIVERLN="#5cb2d6"
ROAD="#7a7a7a"; FREEWAY="#4d4d4d"; INK="#222222"

# ============================================================ PLACES
# keys: slug,name,lat,lon,cat,region,cbd,approx,blurb,hl(list),tip
def P(slug,name,lat,lon,cat,region,blurb,hl,tip,cbd=False,approx=False):
    return dict(slug=slug,name=name,lat=lat,lon=lon,cat=cat,region=region,
                cbd=cbd,approx=approx,blurb=blurb,hl=hl,tip=tip)

PLACES = [
# ---- Perth CBD & Burswood (shown in zoom inset) ----
P("kings-park","Kings Park",-31.960,115.831,"park","Perth CBD",
  "One of the world's largest inner-city parks, rising above the Swan River with sweeping views of the skyline.",
  ["Botanic Garden of WA native plants","War Memorial & State War Memorial precinct","Lotterywest Federation Walkway treetop bridge"],
  "Free entry, open daily. Best at sunset or during the spring wildflower festival (Sept).",cbd=True),
P("elizabeth-quay","Elizabeth Quay",-31.959,115.858,"attraction","Perth CBD",
  "A riverside dining and events precinct wrapped around an inlet, linked by a striking pedestrian bridge.",
  ["BHP Water Park for kids","Bars, restaurants & the Ferris wheel","Ferry to South Perth Zoo"],
  "Great in the evening; markets and events on weekends.",cbd=True),
P("bell-tower","The Bell Tower",-31.960,115.861,"attraction","Perth CBD",
  "A copper-and-glass spire on the waterfront housing the historic bells of St Martin-in-the-Fields, London.",
  ["Ring the bells yourself","360° observation deck","Riverside location by Elizabeth Quay"],
  "Small entry fee; bell-ringing demos daily.",cbd=True),
P("perth-mint","The Perth Mint",-31.958,115.869,"historic","Perth CBD",
  "Australia's oldest operating mint (1899), where you can watch a gold pour and see a giant one-tonne gold coin.",
  ["Live gold pour demonstration","World's largest coin (1 tonne)","Historic 1899 limestone building"],
  "Ticketed tours run through the day.",cbd=True),
P("wa-museum","WA Museum Boola Bardip",-31.947,115.860,"attraction","Perth CBD",
  "The state museum reborn — 'Boola Bardip' means 'many stories' in Noongar — spanning WA's people, land and wildlife.",
  ["Blue whale skeleton","Aboriginal culture galleries","Free general entry"],
  "Free general admission; special exhibitions ticketed.",cbd=True),
P("art-gallery-wa","Art Gallery of WA",-31.949,115.862,"attraction","Perth CBD",
  "The state's premier art collection, from Aboriginal art to Australian and international works, in the Perth Cultural Centre.",
  ["State Art Collection","Rooftop bar with city views","Free general entry"],
  "Free general admission.",cbd=True),
P("state-buildings","State Buildings",-31.954,115.860,"historic","Perth CBD",
  "Beautifully restored 19th-century government buildings now home to COMO The Treasury hotel, bars and restaurants.",
  ["Wildflower & Petition dining","Grand heritage architecture","Long Chim & Post laneway bars"],
  "Free to wander the arcades; dining bookings advised.",cbd=True),
P("supreme-court-gardens","Supreme Court Gardens",-31.958,115.864,"park","Perth CBD",
  "A shady riverside lawn and gardens in the heart of the city, a favourite for summer concerts and picnics.",
  ["Heritage fig trees","Summer concert venue","Steps from the river"],
  "Free, open space; big events in summer.",cbd=True),
P("northbridge","Northbridge",-31.947,115.853,"attraction","Perth CBD",
  "Perth's nightlife and food heartland just north of the railway, packed with restaurants, bars and galleries.",
  ["Chinatown & James St dining","Yagan Square & the markets","Bars and live music"],
  "Liveliest in the evening; very multicultural food scene.",cbd=True),
P("watertown","Watertown Brand Outlet",-31.950,115.842,"attraction","Perth CBD",
  "A large outlet shopping centre on the western edge of the CBD with discount brand stores.",
  ["Discount fashion & brands","Easy CBD access","Undercover shopping"],
  "Open daily; a rainy-day option.",cbd=True),
P("c-restaurant","C Restaurant",-31.953,115.856,"food","Perth CBD",
  "Perth's revolving restaurant, high in St Martins Tower, turning a full circle for 360° city and river views.",
  ["Slowly revolving dining room","Panoramic city views","Fine-dining menu"],
  "Bookings essential; best at dusk.",cbd=True),
P("point-fraser","Point Fraser",-31.960,115.873,"park","Perth CBD",
  "An East Perth foreshore reserve with wetlands, a boardwalk and cafe right on the Swan River.",
  ["Riverside boardwalk & wetlands","Cafe and picnic lawns","Views across to South Perth"],
  "Free; lovely for a morning walk.",cbd=True),
P("waca","WACA Ground",-31.958,115.879,"attraction","Perth CBD",
  "The historic Western Australian Cricket Association ground, a legendary Test venue with a cricket museum.",
  ["Historic cricket Test ground","WACA museum","East Perth location"],
  "Museum & tours on selected days.",cbd=True),
P("optus-stadium","Optus Stadium",-31.951,115.889,"attraction","Perth CBD",
  "Perth's world-class 60,000-seat stadium at Burswood, home to AFL and cricket, ringed by parkland and a riverside plaza.",
  ["AFL, cricket & concerts","Matagarup Bridge & zip-line","Riverside Chevron Parkland"],
  "Event days only for inside; parkland open always.",cbd=True),
P("crown-perth","Crown Perth",-31.960,115.891,"attraction","Perth CBD",
  "A large entertainment complex at Burswood with a casino, hotels, restaurants and a theatre.",
  ["Casino & Crown Towers hotel","Riverside restaurants","Live shows & events"],
  "18+ for the casino; dining open to all.",cbd=True),

# ---- North Coast ----
P("two-rocks","Two Rocks",-31.512,115.588,"beach","North Coast",
  "A laid-back northern coastal town with a marina, fishing and the quirky King Neptune statues at Atlantis.",
  ["Two Rocks Marina","Fishing & boating","Atlantis Marine Park ruins"],
  "Quiet; good for a long drive north up the coast.",approx=False),
P("yanchep","Yanchep National Park",-31.548,115.688,"park","North Coast",
  "A national park famous for its koala boardwalk, caves, wetlands and Noongar heritage, just north of Perth.",
  ["Koala boardwalk","Crystal Cave tours","Loch McNess & walk trails"],
  "Park entry fee applies; cave tours ticketed."),
P("burns-beach","Burns Beach",-31.723,115.717,"beach","North Coast",
  "A relaxed northern beach suburb with a coastal path, cafe and reef for snorkelling.",
  ["Beachfront cafe","Coastal walk to Iluka","Snorkelling on the reef"],
  "Free parking; family-friendly."),
P("mullaloo","Mullaloo Beach",-31.777,115.732,"beach","North Coast",
  "A wide, calm family beach with grassed foreshore, playground and a popular beachfront tavern.",
  ["Gentle swimming beach","Playground & BBQs","Mullaloo Beach Hotel"],
  "Patrolled in summer; great for kids."),
P("hillarys","Hillarys Boat Harbour",-31.822,115.735,"attraction","North Coast",
  "A bustling marina village with a sheltered swimming beach, restaurants, and the AQWA aquarium.",
  ["AQWA — Aquarium of WA","Sorrento Quay dining & shops","Ferry to Rottnest Island"],
  "Free to wander; AQWA & ferries ticketed. Includes AQWA & Sorrento Quay."),
P("trigg","Trigg Beach",-31.867,115.755,"beach","North Coast",
  "Perth's premier surf beach, with a rocky point, cafe and consistent waves.",
  ["Best surf near the city","Bathers Beach cafe","Rockpools at low tide"],
  "Strong currents — swim between the flags."),
P("scarborough","Scarborough Beach",-31.894,115.756,"beach","North Coast",
  "A revitalised beachfront with a huge pool, skate park, amphitheatre and lively bar/restaurant strip.",
  ["Scarborough Beach Pool","Esplanade bars & eateries","Surfing & sunset views"],
  "Free foreshore; busy on summer evenings."),
P("city-beach","City Beach",-31.935,115.752,"beach","North Coast",
  "A broad, family-friendly beach with grassed terraces and upmarket beachfront dining.",
  ["Wide swimming beach","Clancy's & Odyssea dining","Grassed picnic terraces"],
  "Patrolled; good parking."),
P("cottesloe","Cottesloe Beach",-31.996,115.751,"beach","North Coast",
  "Perth's iconic beach — golden sand, Norfolk pines, the Indiana teahouse and famous sunsets.",
  ["Sculpture by the Sea (March)","Indiana teahouse","Great swimming & snorkelling"],
  "Iconic at sunset; arrive early on hot days."),

# ---- Northern Suburbs ----
P("joondalup","Joondalup",-31.744,115.766,"suburb","Northern Suburbs",
  "The bustling centre of Perth's northern suburbs, built around Lake Joondalup with a lively city core.",
  ["Lakeside Joondalup shopping","Central business & dining hub","Yellagonga Regional Park lakes"],
  "Train terminus of the Joondalup line."),
P("joondalup-market","Joondalup Markets",-31.746,115.772,"food","Northern Suburbs",
  "Weekend and twilight markets in Joondalup with fresh produce, street food and local stalls.",
  ["Fresh produce & street food","Local craft stalls","Family atmosphere"],
  "Check days/times before visiting — seasonal.",approx=True),

# ---- Swan Valley ----
P("whiteman-park","Whiteman Park",-31.833,115.945,"park","Swan Valley",
  "A huge bushland park on the edge of the Swan Valley with wildlife, heritage trams, trains and playgrounds.",
  ["Caversham Wildlife Park inside","Heritage tram & train rides","Village, cafes & playgrounds"],
  "Free entry to the park; some attractions ticketed."),
P("caversham","Caversham Wildlife Park",-31.870,115.955,"attraction","Swan Valley",
  "One of WA's best hands-on wildlife parks, inside Whiteman Park — cuddle koalas and hand-feed kangaroos.",
  ["Hold a koala & feed roos","Farm show & wombats","Huge native animal collection"],
  "Ticketed; allow half a day."),
P("sandalford","Sandalford Wines",-31.878,115.958,"food","Swan Valley",
  "A grand, historic Swan Valley winery (est. 1840) known for its cellar door, restaurant and summer concerts.",
  ["Cellar door tastings","Estate restaurant","Big-name summer concerts"],
  "Tastings & dining daily; concerts ticketed."),
P("sittella","Sittella Winery",-31.805,116.020,"food","Swan Valley",
  "A family-owned Herne Hill winery with an award-winning restaurant and valley views.",
  ["Award-winning restaurant","Sparkling & table wines","Vineyard views"],
  "Lunch bookings recommended."),
P("sacred-india-gallery","Sacred India Gallery",-31.795,115.985,"attraction","Swan Valley",
  "A tranquil gallery and Indian-inspired garden in the Swan Valley, with artworks, statues and a cafe.",
  ["Indian art & antiques","Peaceful sculpture gardens","Cafe on site"],
  "Small entry/donation; check opening days.",approx=True),
P("ellenbrook","Ellenbrook",-31.775,115.985,"suburb","Swan Valley",
  "A large master-planned town on the Swan Valley's edge, with a town centre, parks and the new Ellenbrook rail line.",
  ["Ellenbrook Central shopping","Parks & lakes","Gateway to the Swan Valley"],
  "Handy base for exploring the valley."),
P("bailey-brewing","Bailey Brewing Co",-31.830,116.000,"food","Swan Valley",
  "A Swan Valley craft brewery pouring house-made beers with relaxed food and family-friendly grounds.",
  ["House-brewed craft beer","Relaxed beer garden","Wood-fired food"],
  "Great weekend stop on the brewery trail.",approx=True),
P("aurelien","Aurelien",-31.810,116.000,"food","Swan Valley",
  "A Swan Valley dining destination among the vines, part of the region's celebrated food and wine trail.",
  ["Seasonal produce menu","Vineyard surrounds","Swan Valley food trail"],
  "Bookings advised.",approx=True),
P("seven-sins","Seven Sins",-31.840,115.990,"food","Swan Valley",
  "A Swan Valley cellar door / eatery leaning into indulgence — wine, sweets and long lazy lunches.",
  ["Wine tastings","Chocolates & treats","Relaxed valley vibe"],
  "One for a leisurely afternoon.",approx=True),
P("avocado-grove","The Avocado Grove",-31.820,116.010,"food","Swan Valley",
  "A Swan Valley grove and cafe celebrating local produce, with orchard views and farm-fresh fare.",
  ["Farm-fresh cafe fare","Orchard setting","Local produce to buy"],
  "Seasonal — check opening days.",approx=True),
P("guildford","Guildford",-31.900,115.973,"historic","Swan Valley",
  "A historic river town at the gateway to the Swan Valley, full of heritage buildings, antiques and old pubs.",
  ["Heritage main street","Antique & vintage shops","Historic Guildford Hotel"],
  "Free to explore; markets on some weekends."),
P("midland","Midland",-31.888,116.010,"historic","Swan Valley",
  "A regional hub built on the old railway workshops, now a heritage precinct with markets and shopping.",
  ["Midland Railway Workshops heritage","Weekend markets","Regional shopping centre"],
  "Heritage tours of the workshops on some days."),
P("bells-rapids","Bells Rapids",-31.774,116.045,"park","Swan Valley",
  "A scenic reserve where the Swan and Avon rivers meet — bushwalks, granite and the Avon Descent finish nearby.",
  ["Swan River walk trails","Granite outcrops & rapids","Avon Descent viewing (Aug)"],
  "Free; wear sturdy shoes for the trails."),

# ---- Perth Hills ----
P("john-forrest-np","John Forrest National Park",-31.885,116.088,"park","Perth Hills",
  "WA's oldest national park, with waterfalls, a heritage railway tunnel walk and a hilltop tavern.",
  ["National Park Falls","Railway Reserves Heritage Trail","John Forrest Tavern"],
  "Park entry fee; waterfalls best in winter/spring."),
P("lake-leschenaultia","Lake Leschenaultia",-31.878,116.213,"park","Perth Hills",
  "A tranquil man-made lake at Chidlow for swimming, canoeing and camping among the jarrah forest.",
  ["Swimming & canoe hire","Lakeside camping","Bushwalk & bike trails"],
  "Small entry fee; canoe hire seasonal."),
P("mundaring","Mundaring",-31.900,116.167,"hills","Perth Hills",
  "A leafy hills town, a hub for the surrounding forest, trails and the historic Mundaring Weir.",
  ["Village shops & cafes","Gateway to hills trails","Sculpture park nearby"],
  "Nice base for a hills day trip."),
P("mundaring-weir","Mundaring Weir",-31.960,116.170,"attraction","Perth Hills",
  "A historic dam that pumps water 560 km to Kalgoorlie's goldfields — an engineering marvel with a hotel and museum.",
  ["Historic C.Y. O'Connor pipeline","Weir wall & lookout","Mundaring Weir Hotel"],
  "Free to view; museum & hotel nearby."),
P("kalamunda","Kalamunda",-31.976,116.058,"hills","Perth Hills",
  "A charming hills town with a history village, weekend markets, and the start of the Bibbulmun Track.",
  ["Kalamunda History Village","Saturday markets","Bibbulmun Track northern end"],
  "Includes nearby Lesmurdie Falls. Markets Saturday mornings."),
P("lesmurdie","Lesmurdie Falls",-31.995,116.055,"park","Perth Hills",
  "A hills suburb best known for Lesmurdie Falls, which tumble down the Darling Scarp with valley views.",
  ["Lesmurdie Falls walk","Coastal-plain views","Foothills bushland"],
  "Free; falls flow best after winter rain."),
P("carmel","Carmel",-32.020,116.085,"suburb","Perth Hills",
  "A quiet rural-residential pocket of the Perth Hills among orchards and bushland.",
  ["Orchards & small farms","Bushland surrounds","Peaceful drive"],
  "Rural; combine with Pickering Brook wineries.",approx=True),
P("pickering-brook","Pickering Brook",-32.030,116.100,"suburb","Perth Hills",
  "A hills orchard district known for apples, cider and cherry season, with cellar doors and farm gates.",
  ["Apple & cherry orchards","Cider houses","Autumn harvest season"],
  "Best in autumn (cherries early summer)."),
P("core-cider","Core Cider House",-32.025,116.100,"food","Perth Hills",
  "A Pickering Brook orchard and cider house making apple cider from its own trees, with tastings and meals.",
  ["Apple cider tastings","Orchard views","Family-friendly meals"],
  "Cellar door daily; lunch on weekends."),
P("lavender-bistro","Lavender Bistro",-32.020,116.110,"food","Perth Hills",
  "A relaxed Perth Hills eatery among the trees, popular for long lunches and country-style fare.",
  ["Country-style dining","Garden setting","Seasonal menu"],
  "Bookings advised on weekends.",approx=True),
P("bickley-valley","Bickley Valley",-32.022,116.098,"hills","Perth Hills",
  "A pretty hills valley of wineries, orchards and observatories, ideal for a slow food-and-wine wander.",
  ["Boutique wineries","Perth Observatory nearby","Orchard scenery"],
  "Cellar doors mostly open weekends."),
P("roleystone","Roleystone",-32.115,116.072,"park","Perth Hills",
  "A forested hills suburb wrapped around Araluen Botanic Park and the Canning River gorge.",
  ["Araluen Botanic Park","Tulip festival (spring)","Canning River & dam"],
  "Includes Araluen Botanic Park (ticketed)."),
P("jarrahdale","Jarrahdale",-32.335,116.060,"historic","Perth Hills",
  "A historic timber-milling village in the jarrah forest, with heritage cottages, walk trails and a tavern.",
  ["Heritage timber-town buildings","Serpentine forest trails","Millbrook Winery nearby"],
  "Free to explore; great autumn colours."),
P("millbrook-winery","Millbrook Winery",-32.355,116.055,"food","Perth Hills",
  "A picturesque estate winery near Jarrahdale with a lauded restaurant overlooking the dam and gardens.",
  ["Estate restaurant","Lakeside cellar door","Kitchen garden produce"],
  "Lunch bookings essential; scenic drive."),
P("serpentine-falls","Serpentine Falls",-32.362,116.010,"park","Perth Hills",
  "A popular waterfall and swimming hole in Serpentine National Park, with kangaroos and forest trails.",
  ["Waterfall & swimming pool","Resident kangaroos","Forest walk trails"],
  "Park entry fee; can reach capacity on hot days."),
P("secret-garden","Secret Garden",-32.340,116.000,"attraction","Perth Hills",
  "A tucked-away garden retreat on the edge of the hills — greenery, quiet paths and a relaxed cafe.",
  ["Landscaped gardens","Peaceful cafe","Photo-worthy corners"],
  "Check opening days before visiting.",approx=True),

# ---- South of the River ----
P("south-perth","South Perth Foreshore",-31.977,115.853,"attraction","South of River",
  "A riverside foreshore with the best postcard view of the Perth skyline, plus Perth Zoo just behind.",
  ["Best city skyline view","Perth Zoo nearby","Ferry to Elizabeth Quay"],
  "Includes Perth Zoo & the foreshore. Free foreshore; zoo ticketed."),
P("applecross","Applecross",-32.015,115.835,"suburb","South of River",
  "A leafy riverside suburb with a village strip, jetty and the landmark Raffles hotel on the water.",
  ["Riverside walk & jetty","Ardross St cafe strip","Canning Bridge views"],
  "Lovely for a riverside stroll."),
P("point-walter","Point Walter",-32.020,115.788,"park","South of River",
  "A Swan River reserve with a long sandbar (spit), grassy picnic areas and calm swimming.",
  ["Walk out on the sandbar","Picnics & BBQs","Calm river swimming"],
  "Free; sandbar best at low tide."),
P("wireless-hill","Wireless Hill Park",-32.030,115.828,"park","South of River",
  "A bushland hilltop park on a historic radio-telegraph site, superb for wildflowers and city views.",
  ["Spring wildflowers","Telecommunications museum","Panoramic views"],
  "Free; wildflowers peak Sept–Oct."),
P("nedlands","Nedlands",-31.980,115.810,"suburb","South of River",
  "An affluent riverside suburb near UWA, with foreshore parks, jetties and the Captain Stirling strip.",
  ["Swan River foreshore","Near UWA & QEII","Riverside dining"],
  "Pleasant riverside walks."),
P("peppermint-grove","Peppermint Grove",-32.000,115.770,"suburb","South of River",
  "WA's smallest and most exclusive suburb, a green riverside enclave of grand homes near the water.",
  ["Leafy heritage streets","Manning Park & jetty","Near Cottesloe"],
  "A quiet, scenic drive-through."),
P("fremantle","Fremantle",-32.055,115.748,"historic","South of River",
  "Perth's historic port city — heritage streets, markets, breweries and a world-famous prison.",
  ["Fremantle Prison (UNESCO)","Fremantle Markets","The Round House & Fishing Boat Harbour"],
  "Includes the Prison, Round House & Fishing Boat Harbour. Markets Fri–Sun."),
P("coogee","Coogee Beach",-32.115,115.762,"beach","South of River",
  "A calm family beach south of Fremantle with a long jetty, the Omeo dive wreck and a grassed foreshore.",
  ["Omeo shipwreck snorkel trail","Long swimming jetty","Coogee Beach cafe"],
  "Patrolled in summer; great for families."),
P("bibra-lake","Bibra Lake",-32.098,115.825,"park","South of River",
  "A large wetland lake and regional park with a boardwalk, adventure playground and abundant birdlife.",
  ["Adventure playground","Wetland boardwalk & birds","Walk/cycle loop"],
  "Free; big playground for kids."),
P("aubin-grove","Aubin Grove",-32.160,115.855,"suburb","South of River",
  "A newer southern suburb with a train station on the Mandurah line and family parks.",
  ["Train station on Mandurah line","Family parklands","Handy southern base"],
  "Park-and-ride hub for the south.",approx=True),
P("southern-river","Southern River",-32.100,115.950,"suburb","South of River",
  "A growing suburb of parks and wetlands in Perth's south-east, along the Southern River.",
  ["Wetlands & reserves","Family neighbourhoods","Close to Gosnells"],
  "Quiet residential area.",approx=True),
P("harrisdale","Harrisdale",-32.115,115.920,"suburb","South of River",
  "A modern master-planned suburb in the south-east with parks, wetlands and Stockland Harrisdale.",
  ["Piara Waters wetlands nearby","Local shopping","New parklands"],
  "Newer family suburb.",approx=True),
P("piara-waters","Piara Waters",-32.125,115.915,"suburb","South of River",
  "A fast-growing southern suburb next to Harrisdale, with fresh parks, schools and wetland reserves.",
  ["Wetland reserves","Playgrounds & schools","Modern estates"],
  "Pairs with neighbouring Harrisdale.",approx=True),

# ---- Southern Suburbs & Peel ----
P("rockingham","Rockingham",-32.278,115.729,"hills","Southern Suburbs",
  "A coastal city south of Perth with calm swimming beaches, a foreshore strip and wild dolphins offshore.",
  ["Calm swimming foreshore","Dolphin & Penguin Island tours","Waterfront dining"],
  "Gateway to Penguin Island (ferry seasonal)."),
P("baldivis","Baldivis",-32.330,115.820,"suburb","Southern Suburbs",
  "A rapidly growing suburb between Rockingham and the freeway, with big parks and the Baldivis Children's Forest.",
  ["Baldivis Children's Forest","Stockland shopping","Family parklands"],
  "Handy stop off the Kwinana Freeway.",approx=True),
P("penguin-island","Penguin Island",-32.305,115.690,"park","Southern Suburbs",
  "A small island reserve off Rockingham, home to little penguins, sea lions and pelicans, reached by ferry.",
  ["Little penguin colony","Boardwalks & beaches","Sea lion & dolphin cruises"],
  "Island closed June–mid Sept (nesting); ferry ticketed."),
P("secret-harbour","Secret Harbour",-32.410,115.760,"beach","Southern Suburbs",
  "A surf-side southern suburb with a patrolled beach, surf club and a village shopping centre.",
  ["Patrolled surf beach","Surf lifesaving club","Beachside cafes"],
  "Good surf; swim between the flags."),
P("port-kennedy","Port Kennedy",-32.375,115.755,"suburb","Southern Suburbs",
  "A coastal suburb south of Rockingham with beaches, a golf resort and a scientific bushland park.",
  ["Long sandy beaches","Golf & foreshore","Port Kennedy bushland"],
  "Quiet coastal drive.",approx=True),
P("mandurah","Mandurah",-32.528,115.722,"hills","Peel Region",
  "A relaxed waterway city an hour south of Perth, famous for its canals, dolphins, crabbing and foreshore.",
  ["Dolphin & canal cruises","Blue-manna crabbing","Mandurah Foreshore & markets"],
  "End of the Mandurah rail line; great day trip."),
P("pinjarra","Pinjarra",-32.630,115.875,"hills","Peel Region",
  "A historic town on the Murray River in the Peel region, with heritage buildings and a scenic steam railway.",
  ["Murray River picnic spots","Hotham Valley steam train","Country heritage town"],
  "Combine with Edenvale Heritage Precinct."),
P("edenvale-heritage","Edenvale Heritage Precinct",-32.628,115.872,"historic","Peel Region",
  "Pinjarra's restored heritage precinct — a homestead, gardens, tearooms and craft shops beside the Murray.",
  ["Historic Edenvale homestead","Tearooms & craft shops","Riverside gardens"],
  "Free grounds; tearooms open most days."),
P("koala-centre","Cohunu Koala Park",-32.220,116.020,"attraction","Perth Hills",
  "A wildlife park near Byford where you can hold a koala and meet kangaroos, deer and birds.",
  ["Hold a koala","Miniature railway","Hand-feed the animals"],
  "Ticketed; koala holding at set times.",approx=True),
P("serpentine","Serpentine",-32.365,115.980,"hills","Perth Hills",
  "A small town below the Darling Scarp, gateway to Serpentine Falls, the dam and jarrah-forest trails.",
  ["Gateway to Serpentine Falls","Serpentine Dam drive","Country pub & shops"],
  "Base for the national park and dam."),

# ---- Nature ----
P("herdsman-lake","Herdsman Lake",-31.925,115.805,"park","Nature",
  "A large wetland reserve close to the city with a wildlife centre and a flat cycle/walk loop rich in birdlife.",
  ["Wildlife discovery centre","Birdwatching hides","Cycle & walk loop"],
  "Free; excellent for birdwatchers."),
P("bold-park","Bold Park",-31.945,115.775,"park","Nature",
  "A large natural bushland reserve near City Beach, with the Reabold Hill lookout over city and sea.",
  ["Reabold Hill lookout","Bushland walk trails","Spring wildflowers"],
  "Free; highest natural point near the coast."),

# ---- Home ----
P("home","Home — 2 Zinnia Way, Willetton",-32.052,115.890,"home","South of River",
  "Home base for all the adventures — 2 Zinnia Way, Willetton, in Perth's leafy southern suburbs.",
  ["Start & end of every trip","Willetton, south of the river","Near the Canning River & Kwinana Fwy"],
  "This is home! Plan your next outing from here."),
]

# de-dupe slug guard
_seen=set()
for p in PLACES:
    assert p["slug"] not in _seen, p["slug"]
    _seen.add(p["slug"])

CBD_SLUGS = [p["slug"] for p in PLACES if p["cbd"]]

# ============================================================ GEOMETRY
COAST=[(-31.44,115.585),(-31.55,115.627),(-31.62,115.660),(-31.72,115.700),
 (-31.78,115.720),(-31.822,115.727),(-31.87,115.748),(-31.895,115.750),
 (-31.935,115.748),(-31.996,115.748),(-32.055,115.738),(-32.115,115.758),
 (-32.20,115.765),(-32.278,115.720),(-32.34,115.735),(-32.41,115.752),
 (-32.47,115.735),(-32.55,115.715),(-32.66,115.700)]
SWAN=[(-32.052,115.745),(-32.032,115.760),(-32.012,115.782),(-32.022,115.792),
 (-32.000,115.802),(-31.985,115.822),(-31.978,115.848),(-31.960,115.860),
 (-31.955,115.888),(-31.945,115.908),(-31.928,115.935),(-31.905,115.962),
 (-31.882,115.996),(-31.855,116.020),(-31.800,116.043)]
CANNING=[(-31.998,115.828),(-32.015,115.842),(-32.028,115.862),(-32.040,115.878),
 (-32.052,115.898),(-32.020,115.918),(-32.010,115.940)]
MURRAY=[(-32.53,115.72),(-32.57,115.78),(-32.60,115.83),(-32.628,115.872),(-32.64,115.92)]
ROADS=[
 ("Mitchell Fwy",[(-31.955,115.853),(-31.905,115.815),(-31.850,115.795),(-31.800,115.790),(-31.745,115.795),(-31.690,115.760)],3,True),
 ("Marmion Ave",[(-31.690,115.760),(-31.640,115.700),(-31.560,115.640),(-31.512,115.600)],1,False),
 ("Kwinana Fwy",[(-31.965,115.855),(-32.010,115.856),(-32.055,115.855),(-32.105,115.845),(-32.160,115.835),(-32.230,115.835)],3,True),
 ("Forrest Hwy",[(-32.230,115.835),(-32.320,115.800),(-32.420,115.775),(-32.520,115.745),(-32.62,115.83)],1,False),
 ("Roe Hwy",[(-31.895,116.010),(-31.950,115.980),(-32.005,115.960),(-32.060,115.935),(-32.100,115.905)],2,True),
 ("Tonkin Hwy",[(-31.870,115.975),(-31.960,115.975),(-32.050,115.978),(-32.120,115.978)],2,True),
 ("Great Eastern Hwy",[(-31.955,115.888),(-31.930,115.940),(-31.900,115.992),(-31.900,116.060),(-31.900,116.160)],3,False),
 ("Albany Hwy",[(-31.982,115.900),(-32.030,115.952),(-32.085,116.002),(-32.140,116.012)],2,False),
 ("Canning Hwy",[(-32.055,115.748),(-32.020,115.800),(-31.998,115.832),(-31.980,115.856)],1,False),
 ("Reid Hwy",[(-31.870,115.760),(-31.870,115.840),(-31.870,115.918),(-31.870,115.980)],2,False),
 ("West Coast Hwy",[(-31.870,115.753),(-31.910,115.757),(-31.955,115.757),(-31.995,115.754)],1,False),
]

# ============================================================ SVG HELPERS
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def path_from(pts, close_left=None):
    d=""
    for i,(la,lo) in enumerate(pts):
        x,y=proj(la,lo); d+=("M" if i==0 else "L")+f"{x:.2f},{y:.2f} "
    if close_left is not None:
        fx,fy=proj(*pts[0]); lx,ly=proj(*pts[-1])
        d+=f"L{close_left:.2f},{ly:.2f} L{close_left:.2f},{fy:.2f} Z"
    return d

def star(cx,cy,ro,ri,n,fill,stroke,sw):
    pts=[]
    for i in range(n*2):
        ang=-math.pi/2+i*math.pi/n; rr=ro if i%2==0 else ri
        pts.append(f"{cx+rr*math.cos(ang):.2f},{cy+rr*math.sin(ang):.2f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def marker_shape(mx,my,cat,r=1.9):
    c=COL[cat]
    if cat=="park":
        return (f'<path d="M{mx:.2f},{my-r-0.3:.2f} L{mx+r+0.2:.2f},{my+r:.2f} L{mx-r-0.2:.2f},{my+r:.2f} Z" '
                f'fill="{c}" stroke="#fff" stroke-width="0.5"/>')
    if cat=="beach":
        return f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="{r}" fill="{c}" stroke="#fff" stroke-width="0.5"/>'
    if cat=="attraction":
        return (f'<path d="M{mx:.2f},{my-r-0.2:.2f} L{mx+r+0.2:.2f},{my:.2f} L{mx:.2f},{my+r+0.2:.2f} '
                f'L{mx-r-0.2:.2f},{my:.2f} Z" fill="{c}" stroke="#fff" stroke-width="0.5"/>')
    if cat=="hills":
        s=r*0.95
        return f'<rect x="{mx-s:.2f}" y="{my-s:.2f}" width="{2*s:.2f}" height="{2*s:.2f}" rx="0.3" fill="{c}" stroke="#fff" stroke-width="0.5"/>'
    if cat=="historic":
        return star(mx,my,r+0.4,r*0.5,5,c,"#fff",0.4)
    if cat=="food":
        # wine-red circle with inner ring
        return (f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="{r}" fill="{c}" stroke="#fff" stroke-width="0.5"/>'
                f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="{r*0.4:.2f}" fill="#fff"/>')
    if cat=="suburb":
        return f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="{r*0.75:.2f}" fill="#fff" stroke="{c}" stroke-width="0.8"/>'
    return f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="{r}" fill="{c}"/>'

# ============================================================ LABEL LAYOUT
def layout_labels(markers, fs, bounds, seed=None, dot_r=2.4, char=0.55):
    """markers: list of (mx,my,text). Returns per-marker dict {ax,ay,anchor,w,h,lead}.
    Greedy collision avoidance: try 8 directions at growing radii; draw a leader when displaced."""
    x0b,y0b,x1b,y1b = bounds
    obstacles = list(seed or [])
    for mx,my,_ in markers:
        obstacles.append((mx-dot_r,my-dot_r,mx+dot_r,my+dot_r))
    def hit(b):
        for p in obstacles:
            if not (b[2]<=p[0] or b[0]>=p[2] or b[3]<=p[1] or b[1]>=p[3]): return True
        return False
    def inb(b):
        return b[0]>=x0b and b[2]<=x1b and b[1]>=y0b and b[3]<=y1b
    # process densest-neighbourhood markers last so isolated ones grab close spots first
    def nn(i):
        mx,my,_=markers[i]; d=0
        for j,(nx,ny,_) in enumerate(markers):
            if j!=i and abs(nx-mx)<14 and abs(ny-my)<14: d+=1
        return d
    order = sorted(range(len(markers)), key=lambda i:(nn(i), markers[i][1], markers[i][0]))
    out=[None]*len(markers)
    dirs=[(1,0,'start'),(-1,0,'end'),(0,-1,'middle'),(0,1,'middle'),
          (1,-0.85,'start'),(-1,-0.85,'end'),(1,0.85,'start'),(-1,0.85,'end')]
    for i in order:
        mx,my,text=markers[i]
        w=len(text)*fs*char+1.2; h=fs+0.8
        placed=False
        for r in (dot_r+1.0, dot_r+3.0, dot_r+6.0, dot_r+9.5, dot_r+13.5, dot_r+18.5, dot_r+24.5, dot_r+31):
            for dx,dy,anch in dirs:
                ay=my+dy*r
                if anch=='start': ax=mx+dx*r; box=(ax,ay-h/2,ax+w,ay+h/2)
                elif anch=='end':  ax=mx+dx*r; box=(ax-w,ay-h/2,ax,ay+h/2)
                else:              ax=mx;      box=(mx-w/2,ay-h/2,mx+w/2,ay+h/2)
                if inb(box) and not hit(box):
                    obstacles.append(box)
                    lead=None
                    if math.hypot(ax-mx,ay-my) > dot_r+2.2:
                        tx = ax-0.4 if anch=='start' else (ax+0.4 if anch=='end' else ax)
                        lead=(mx,my,tx,ay)
                    out[i]=dict(ax=ax,ay=ay,anchor=anch,w=w,h=h,lead=lead)
                    placed=True; break
            if placed: break
        if not placed:
            ax=mx+dot_r+1.0; box=(ax,my-h/2,ax+w,my+h/2); obstacles.append(box)
            out[i]=dict(ax=ax,ay=my,anchor='start',w=w,h=h,lead=None)
    return out

def emit_labels(add, markers, lay, fs, halo="#fff", weight="600", fill=None, cls=""):
    fill = fill or INK
    for (mx,my,text),info in zip(markers,lay):
        if info["lead"]:
            x1,y1,x2,y2=info["lead"]
            add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#b6b6b6" stroke-width="0.3"/>')
    for (mx,my,text),info in zip(markers,lay):
        c=f' class="{cls}"' if cls else ""
        add(f'<text x="{info["ax"]:.2f}" y="{info["ay"]+info["h"]*0.30:.2f}" font-size="{fs}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{info["anchor"]}"{c} '
            f'paint-order="stroke" stroke="{halo}" stroke-width="1.0" stroke-linejoin="round">{esc(text)}</text>')

# ============================================================ PRINT MAP
def build_print_map():
    svg=[]; add=svg.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
        f'viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
    add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')
    add(f'<clipPath id="mapclip"><rect x="{MX0}" y="{MY0}" width="{MW}" height="{MH}"/></clipPath>')
    add('<g clip-path="url(#mapclip)">')
    add(f'<path d="{path_from(COAST,close_left=-40)}" fill="{OCEAN}"/>')
    for riv in (SWAN,CANNING,MURRAY):
        add(f'<path d="{path_from(riv)}" fill="none" stroke="{RIVER}" stroke-width="3.4" stroke-linecap="round"/>')
        add(f'<path d="{path_from(riv)}" fill="none" stroke="{RIVERLN}" stroke-width="0.5" stroke-linecap="round"/>')
    road_labels=[]
    for name,pts,li,fw in ROADS:
        d=path_from(pts); w=2.2 if fw else 1.5; col=FREEWAY if fw else ROAD
        if fw: add(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w+1.4}" stroke-linecap="round" stroke-linejoin="round"/>')
        add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
        la,lo=pts[li]; lx,ly=proj(la,lo); road_labels.append((name,lx,ly))
    add('</g>')
    ox,oy=proj(-31.95,115.60)
    add(f'<text x="{ox:.1f}" y="{oy:.1f}" font-size="6" fill="#3b8fb5" font-style="italic" font-weight="700" '
        f'opacity="0.75" transform="rotate(-90 {ox:.1f} {oy:.1f})" text-anchor="middle">INDIAN OCEAN</text>')
    for name,lx,ly in road_labels:
        if MX0<=lx<=MX0+MW and MY0<=ly<=MY0+MH:
            add(f'<text x="{lx:.1f}" y="{ly-1.2:.1f}" font-size="2.7" fill="#3d3d3d" font-style="italic" '
                f'text-anchor="middle" paint-order="stroke" stroke="#fff" stroke-width="1.0" stroke-linejoin="round">{esc(name)}</text>')

    LFS=2.9
    render=[p for p in PLACES if not p["cbd"] and p["cat"]!="home"]
    render=render+[{"lat":-31.953,"lon":115.860,"cat":"attraction","name":"Perth CBD"}]
    hp=next(p for p in PLACES if p["cat"]=="home"); hx,hy=proj(hp["lat"],hp["lon"])
    seed=[]
    for name,lx,ly in road_labels:
        w=len(name)*2.7*0.55; seed.append((lx-w/2,ly-3.4,lx+w/2,ly+0.6))
    seed.append((hx-7,hy-9,hx+20,hy+10))   # reserve home marker + its labels
    markers=[(*proj(p["lat"],p["lon"]),p["name"]) for p in render]
    lay=layout_labels(markers,LFS,(MX0+0.5,MY0+0.5,MX0+MW-0.5,MY0+MH-0.5),seed=seed)
    for p in render:
        mx,my=proj(p["lat"],p["lon"]); add(marker_shape(mx,my,p["cat"]))
    emit_labels(add,markers,lay,LFS)

    # HOME
    add(f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="4.6" fill="#fff" stroke="{COL["home"]}" stroke-width="0.8"/>')
    add(star(hx,hy,4.2,1.9,5,COL["home"],"#fff",0.6))
    add(f'<text x="{hx:.2f}" y="{hy-6.5:.2f}" font-size="4.2" font-weight="800" fill="{COL["home"]}" '
        f'text-anchor="middle" paint-order="stroke" stroke="#fff" stroke-width="1.4">HOME</text>')
    add(f'<text x="{hx:.2f}" y="{hy+8.2:.2f}" font-size="2.9" font-weight="700" fill="{COL["home"]}" '
        f'text-anchor="middle" paint-order="stroke" stroke="#fff" stroke-width="1.1">2 Zinnia Way, Willetton</text>')

    # scale bar + N
    sb_x,sb_y=MX0+6,MY0+MH-10; km10=10.0/111.0*SCALE
    add(f'<rect x="{sb_x}" y="{sb_y}" width="{km10:.2f}" height="1.8" fill="{INK}"/>')
    add(f'<rect x="{sb_x}" y="{sb_y}" width="{km10/2:.2f}" height="1.8" fill="#fff" stroke="{INK}" stroke-width="0.3"/>')
    add(f'<text x="{sb_x}" y="{sb_y-1.5:.1f}" font-size="2.8" fill="{INK}">0</text>')
    add(f'<text x="{sb_x+km10:.1f}" y="{sb_y-1.5:.1f}" font-size="2.8" fill="{INK}" text-anchor="middle">10 km</text>')
    nax,nay=MX0+MW-12,MY0+14
    add(f'<polygon points="{nax},{nay-7} {nax-3},{nay+3} {nax},{nay} {nax+3},{nay+3}" fill="{INK}"/>')
    add(f'<text x="{nax}" y="{nay+8}" font-size="3.6" font-weight="800" fill="{INK}" text-anchor="middle">N</text>')
    add(f'<rect x="{MX0}" y="{MY0}" width="{MW}" height="{MH}" fill="none" stroke="#333" stroke-width="0.6"/>')

    # ---------- title + side panel ----------
    add(f'<text x="{PX0-2}" y="26" font-size="15" font-weight="900" fill="{INK}">MY PERTH</text>')
    add(f'<text x="{PX0-2}" y="42" font-size="15" font-weight="900" fill="{INK}">ADVENTURE MAP</text>')
    add(f'<text x="{PX0-2}" y="52" font-size="4.2" fill="#555" font-style="italic">A memory map for exploring &amp; remembering Perth, WA</text>')
    add(f'<line x1="{PX0-2}" y1="58" x2="{W-8}" y2="58" stroke="#333" stroke-width="0.5"/>')
    add(f'<text x="{MX0+2}" y="{MY0-3}" font-size="5" font-weight="800" fill="#444">Greater Perth  ·  major roads, rivers &amp; landmarks</text>')

    cy=70.0; lx=PX0-1
    def ptext(x,y,s,size=4.2,weight="400",fill=INK,style="normal"):
        add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" font-style="{style}">{s}</text>')
    ptext(PX0-2,cy,"MAP KEY",6,"800"); cy+=7
    for cat in ["park","beach","attraction","hills","historic","food","suburb"]:
        add(marker_shape(lx+1.6,cy-1.4,cat,r=1.9)); ptext(lx+6,cy,esc(CAT_LABEL[cat]),4.1,"500"); cy+=5.6
    add(star(lx+1.6,cy-1.4,2.4,1.1,5,COL["home"],"#fff",0.4)); ptext(lx+6,cy,"HOME (Willetton)",4.1,"700",COL["home"]); cy+=6.2
    add(f'<line x1="{lx}" y1="{cy-1.4}" x2="{lx+4}" y2="{cy-1.4}" stroke="{FREEWAY}" stroke-width="2.2"/>'); ptext(lx+6,cy,"Freeway",4.1,"500"); cy+=5.2
    add(f'<line x1="{lx}" y1="{cy-1.4}" x2="{lx+4}" y2="{cy-1.4}" stroke="{ROAD}" stroke-width="1.5"/>'); ptext(lx+6,cy,"Highway",4.1,"500"); cy+=5.2
    add(f'<line x1="{lx}" y1="{cy-1.4}" x2="{lx+4}" y2="{cy-1.4}" stroke="{RIVER}" stroke-width="3"/>'); ptext(lx+6,cy,"River / ocean",4.1,"500"); cy+=8

    # CBD inset
    ptext(PX0-2,cy,"PERTH CBD &amp; BURSWOOD (zoom)",4.6,"800"); cy+=4
    bx0,by0,bw,bh=PX0-2,cy,PW+2,74.0
    add(f'<rect x="{bx0}" y="{by0}" width="{bw}" height="{bh}" fill="#f4fafd" stroke="#333" stroke-width="0.5" rx="1"/>')
    cbd=[p for p in PLACES if p["cbd"]]
    clat=[p["lat"] for p in cbd]; clon=[p["lon"] for p in cbd]
    la_min,la_max=min(clat)-0.004,max(clat)+0.004; lo_min,lo_max=min(clon)-0.004,max(clon)+0.004
    def cbdproj(la,lo):
        sx=(bw-8)/((lo_max-lo_min)*COSLAT); sy=(bh-10)/(la_max-la_min); s=min(sx,sy)
        uw=(lo_max-lo_min)*COSLAT*s; uh=(la_max-la_min)*s
        offx=bx0+4+((bw-8)-uw)/2; offy=by0+5+((bh-10)-uh)/2
        return offx+(lo-lo_min)*COSLAT*s, offy+(la_max-la)*s
    dr=""
    for i,(la,lo) in enumerate([(-31.962,115.845),(-31.960,115.858),(-31.957,115.875),(-31.953,115.892)]):
        x,y=cbdproj(la,lo); dr+=("M" if i==0 else "L")+f"{x:.1f},{y:.1f} "
    add(f'<path d="{dr}" fill="none" stroke="{RIVER}" stroke-width="2.4" stroke-linecap="round"/>')
    cbd_markers=[]
    for p in cbd:
        mx,my=cbdproj(p["lat"],p["lon"])
        add(f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="1.3" fill="{COL[p["cat"]]}" stroke="#fff" stroke-width="0.4"/>')
        nm=p["name"].replace(" Boola Bardip","").replace(" Brand Outlet","").replace(" Ground","")
        cbd_markers.append((mx,my,nm))
    clay=layout_labels(cbd_markers,2.3,(bx0+1,by0+1,bx0+bw-1,by0+bh-1),dot_r=1.5,char=0.52)
    emit_labels(add,cbd_markers,clay,2.3,halo="#f4fafd")
    cy=by0+bh+7

    # Favourites
    ptext(PX0-2,cy,"★ FAVOURITE PLACES (TOP 10)",5,"800"); cy+=6.5
    for i in range(1,11):
        add(f'<text x="{PX0-2}" y="{cy:.1f}" font-size="4.2" font-weight="700" fill="{INK}">{i}.</text>')
        add(f'<line x1="{PX0+6}" y1="{cy:.1f}" x2="{W-10}" y2="{cy:.1f}" stroke="#bbb" stroke-width="0.4"/>'); cy+=7.5
    cy+=2
    ptext(PX0-2,cy,"HOW TO USE",5,"800"); cy+=5.6
    for t in ["Mark each place after you visit it.","Add the date + a short memory note.",
              "Colour it in or add a sticker.","Star your favourite experiences."]:
        add(f'<text x="{PX0-2}" y="{cy:.1f}" font-size="3.6" fill="#333">• {esc(t)}</text>'); cy+=5.0
    add('</svg>')
    return "\n".join(svg)

# ============================================================ INTERACTIVE MAP SVG (map area only, clickable)
def build_interactive_svg():
    # viewBox focused on the map area
    vb_x,vb_y,vb_w,vb_h = MX0-3, MY0-6, MW+6, MH+12
    svg=[]; add=svg.append
    add(f'<svg id="perthmap" xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x} {vb_y} {vb_w} {vb_h}" '
        f'font-family="Inter, Arial, Helvetica, sans-serif" preserveAspectRatio="xMidYMid meet">')
    add(f'<rect x="{vb_x}" y="{vb_y}" width="{vb_w}" height="{vb_h}" fill="var(--map-bg,#ffffff)"/>')
    add(f'<clipPath id="mc"><rect x="{MX0}" y="{MY0}" width="{MW}" height="{MH}"/></clipPath>')
    add('<g id="viewport">')
    add(f'<g clip-path="url(#mc)">')
    add(f'<path d="{path_from(COAST,close_left=-40)}" fill="{OCEAN}"/>')
    for riv in (SWAN,CANNING,MURRAY):
        add(f'<path d="{path_from(riv)}" fill="none" stroke="{RIVER}" stroke-width="3.4" stroke-linecap="round"/>')
    for name,pts,li,fw in ROADS:
        d=path_from(pts); w=2.2 if fw else 1.5; col=FREEWAY if fw else ROAD
        if fw: add(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w+1.4}" stroke-linecap="round" stroke-linejoin="round"/>')
        add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    add('</g>')  # clip
    ox,oy=proj(-31.95,115.60)
    add(f'<text x="{ox:.1f}" y="{oy:.1f}" font-size="6" fill="#3b8fb5" font-style="italic" font-weight="700" '
        f'opacity="0.6" transform="rotate(-90 {ox:.1f} {oy:.1f})" text-anchor="middle">INDIAN OCEAN</text>')
    # markers (clickable) with collision-avoided labels + leader lines
    LFS=2.7
    pts=[p for p in PLACES if not p["cbd"] and p["cat"]!="home"]
    hp=next(p for p in PLACES if p["cat"]=="home"); hx,hy=proj(hp["lat"],hp["lon"])
    seed=[(hx-8,hy-7,hx+16,hy+8)]  # reserve home + its HOME label
    markers=[(*proj(p["lat"],p["lon"]),p["name"]) for p in pts]
    lay=layout_labels(markers,LFS,(MX0+0.5,MY0+0.5,MX0+MW-0.5,MY0+MH-0.5),seed=seed,dot_r=2.6)
    for p,(mx,my,text),info in zip(pts,markers,lay):
        lead=""
        if info["lead"]:
            x1,y1,x2,y2=info["lead"]
            lead=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#b6b6b6" stroke-width="0.3" class="lead"/>'
        lab=(f'<text x="{info["ax"]:.2f}" y="{info["ay"]+info["h"]*0.30:.2f}" font-size="{LFS}" font-weight="600" '
             f'fill="var(--label,#222)" text-anchor="{info["anchor"]}" paint-order="stroke" '
             f'stroke="var(--label-halo,#fff)" stroke-width="1.0" class="mlabel">{esc(text)}</text>')
        add(f'<a href="place.html?slug={p["slug"]}" class="mk" data-slug="{p["slug"]}" '
            f'data-cat="{p["cat"]}" data-name="{esc(p["name"])}"><title>{esc(p["name"])}</title>{lead}'
            f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="5" fill="transparent"/>{marker_shape(mx,my,p["cat"],r=2.2)}{lab}</a>')
    # HOME last (on top)
    hlab=(f'<text x="{hx:.2f}" y="{hy-6.2:.2f}" font-size="3.4" font-weight="800" fill="{COL["home"]}" '
          f'text-anchor="middle" paint-order="stroke" stroke="var(--label-halo,#fff)" stroke-width="1.3" class="mlabel">HOME</text>')
    add(f'<a href="place.html?slug=home" class="mk" data-slug="home" data-cat="home" data-name="{esc(hp["name"])}">'
        f'<title>{esc(hp["name"])}</title>'
        f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="6" fill="transparent"/>'
        f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="4.6" fill="#fff" stroke="{COL["home"]}" stroke-width="0.8"/>'
        f'{star(hx,hy,4.2,1.9,5,COL["home"],"#fff",0.6)}{hlab}</a>')
    add('</g>')  # viewport
    # scale bar (fixed, outside viewport)
    sb_x,sb_y=MX0+6,MY0+MH-6; km10=10.0/111.0*SCALE
    add(f'<g opacity="0.9"><rect x="{sb_x}" y="{sb_y}" width="{km10:.2f}" height="1.8" fill="{INK}"/>'
        f'<rect x="{sb_x}" y="{sb_y}" width="{km10/2:.2f}" height="1.8" fill="#fff" stroke="{INK}" stroke-width="0.3"/>'
        f'<text x="{sb_x+km10/2:.1f}" y="{sb_y-1.2:.1f}" font-size="2.8" fill="var(--label,#222)" text-anchor="middle">10 km</text></g>')
    add('</svg>')
    return "\n".join(svg)

def build_cbd_inset_svg():
    cbd=[p for p in PLACES if p["cbd"]]
    clat=[p["lat"] for p in cbd]; clon=[p["lon"] for p in cbd]
    la_min,la_max=min(clat)-0.004,max(clat)+0.004; lo_min,lo_max=min(clon)-0.004,max(clon)+0.004
    Wc,Hc=300.0,150.0
    def cp(la,lo):
        sx=(Wc-20)/((lo_max-lo_min)*COSLAT); sy=(Hc-16)/(la_max-la_min); s=min(sx,sy)
        uw=(lo_max-lo_min)*COSLAT*s; uh=(la_max-la_min)*s
        offx=10+((Wc-20)-uw)/2; offy=8+((Hc-16)-uh)/2
        return offx+(lo-lo_min)*COSLAT*s, offy+(la_max-la)*s
    svg=[]; add=svg.append
    add(f'<svg id="cbdmap" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wc} {Hc}" '
        f'font-family="Inter, Arial, sans-serif" preserveAspectRatio="xMidYMid meet">')
    add(f'<rect x="0" y="0" width="{Wc}" height="{Hc}" fill="var(--inset-bg,#eef7fb)" rx="4"/>')
    dr=""
    for i,(la,lo) in enumerate([(-31.962,115.845),(-31.960,115.858),(-31.957,115.875),(-31.953,115.892)]):
        x,y=cp(la,lo); dr+=("M" if i==0 else "L")+f"{x:.1f},{y:.1f} "
    add(f'<path d="{dr}" fill="none" stroke="{RIVER}" stroke-width="4" stroke-linecap="round"/>')
    cmk=[]
    for p in cbd:
        mx,my=cp(p["lat"],p["lon"]); nm=p["name"].replace(" Boola Bardip","").replace(" Brand Outlet","").replace(" Ground","")
        cmk.append((mx,my,nm,p))
    markers=[(m[0],m[1],m[2]) for m in cmk]
    lay=layout_labels(markers,3.2,(4,4,Wc-4,Hc-4),dot_r=2.6,char=0.52)
    for (mx,my,nm,p),info in zip(cmk,lay):
        lead=""
        if info["lead"]:
            x1,y1,x2,y2=info["lead"]
            lead=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#a9c4d2" stroke-width="0.4"/>'
        add(f'<a href="place.html?slug={p["slug"]}" class="mk" data-slug="{p["slug"]}" data-cat="{p["cat"]}" data-name="{esc(p["name"])}">'
            f'<title>{esc(p["name"])}</title>{lead}'
            f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="4.5" fill="transparent"/>'
            f'<circle cx="{mx:.2f}" cy="{my:.2f}" r="2.4" fill="{COL[p["cat"]]}" stroke="#fff" stroke-width="0.6"/>'
            f'<text x="{info["ax"]:.2f}" y="{info["ay"]+info["h"]*0.30:.2f}" font-size="3.2" font-weight="600" '
            f'fill="var(--label,#222)" text-anchor="{info["anchor"]}" paint-order="stroke" '
            f'stroke="var(--inset-bg,#eef7fb)" stroke-width="1.0" class="mlabel">{esc(nm)}</text></a>')
    add('</svg>')
    return "\n".join(svg)

# ============================================================ INDEX.HTML
REGION_ORDER=["Perth CBD","North Coast","Northern Suburbs","Swan Valley","Perth Hills",
              "South of River","Southern Suburbs","Peel Region","Nature"]
def build_index_html():
    map_svg=build_interactive_svg()
    cbd_svg=build_cbd_inset_svg()
    # grouped list
    groups={}
    for p in PLACES:
        groups.setdefault(p["region"],[]).append(p)
    list_html=[]
    for reg in REGION_ORDER + [r for r in groups if r not in REGION_ORDER]:
        if reg not in groups: continue
        items=sorted(groups[reg], key=lambda x:x["name"])
        list_html.append(f'<section class="reg" data-region="{esc(reg)}"><h3>{esc(reg)}</h3><ul>')
        for p in items:
            list_html.append(
                f'<li><a href="place.html?slug={p["slug"]}" data-name="{esc(p["name"].lower())}">'
                f'<span class="dot" style="--c:{COL[p["cat"]]}"></span>{esc(p["name"])}</a></li>')
        list_html.append('</ul></section>')
    list_html="\n".join(list_html)
    legend="".join(
        f'<span class="lg"><span class="dot" style="--c:{COL[c]}"></span>{esc(CAT_LABEL[c])}</span>'
        for c in ["park","beach","attraction","hills","historic","food","suburb","home"])
    total=len([p for p in PLACES if p["cat"]!="home"])
    html=f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>My Perth Adventure Map</title>
<link rel="stylesheet" href="css/styles.css">
</head><body>
<header class="topbar">
  <div class="brand"><span class="pin">★</span><div>
    <h1>My Perth Adventure Map</h1>
    <p>Tap any place to see photos &amp; info · {total} spots across Greater Perth</p></div></div>
  <input id="search" type="search" placeholder="Search a place…" autocomplete="off">
</header>
<main class="layout">
  <div class="mapwrap">
    <div class="mapcanvas" id="mapcanvas">{map_svg}</div>
    <div class="mapctrl">
      <button id="zin" title="Zoom in">+</button>
      <button id="zout" title="Zoom out">−</button>
      <button id="zreset" title="Reset view">⌂</button>
    </div>
    <div class="legend">{legend}</div>
    <div class="inset">
      <h4>Perth CBD &amp; Burswood</h4>
      {cbd_svg}
    </div>
  </div>
  <aside class="sidebar" id="sidebar">
    <h2>All places</h2>
    <div class="list">{list_html}</div>
  </aside>
</main>
<footer><p>Home base: <strong>2 Zinnia Way, Willetton</strong> ⭐ · Built for exploring &amp; remembering Perth.</p></footer>
<script src="js/app.js"></script>
</body></html>"""
    return html

# ============================================================ WRITE ALL
def write(path, content):
    full=os.path.join(HERE,path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full,"w",encoding="utf-8") as f: f.write(content)

def main():
    # print map
    pm=build_print_map()
    write("print/perth_adventure_map.svg", pm)
    write("print/perth_adventure_map.html",
        "<!doctype html><html><head><meta charset='utf-8'><title>Perth Adventure Map (A2)</title>"
        "<style>@page{size:A2 portrait;margin:0}html,body{margin:0;background:#eee}"
        ".wrap{display:flex;justify-content:center;padding:20px}svg{box-shadow:0 4px 20px rgba(0,0,0,.2);background:#fff;width:420mm;height:594mm}"
        "@media print{.wrap{padding:0}svg{box-shadow:none}body{background:#fff}}</style></head>"
        "<body><div class='wrap'>"+pm+"</div></body></html>")
    # data.js
    slim=[{k:p[k] for k in ("slug","name","lat","lon","cat","region","approx","blurb","hl","tip")} for p in PLACES]
    write("js/data.js","// auto-generated by build_site.py\nwindow.PERTH_PLACES = "+json.dumps(slim, ensure_ascii=False, indent=1)+";\n"
          "window.PERTH_CAT = "+json.dumps({**COL}, ensure_ascii=False)+";\n"
          "window.PERTH_CATLABEL = "+json.dumps(CAT_LABEL, ensure_ascii=False)+";\n")
    # index
    write("index.html", build_index_html())
    print(f"OK  places={len(PLACES)}  cbd={len(CBD_SLUGS)}  regions={len(set(p['region'] for p in PLACES))}")

if __name__=="__main__":
    main()
