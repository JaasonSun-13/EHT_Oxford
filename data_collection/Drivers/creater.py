import pandas as pd
import numpy as np
import random as random
from datetime import datetime, timedelta


def generate_future_dates(df_driver, num_driver=600, days_in_fututre=14, busy_driver=50):
    avalability = [1]*busy_driver + [0]*(num_driver - busy_driver)
    today = datetime.today().date()
    headers = [today + timedelta(days=i) for i in range(15)]
    for tick in headers:
        random.shuffle(avalability)
        df_driver[f'{tick}'] = avalability
    return print(f'avalability generated for future {days_in_fututre} days')


def creat_drivers(driver_city="Oxford"):

    df_driver = pd.DataFrame()
    languages = [
        "Mandarin Chinese",
        "Cantonese",
        "Hindi",
        "Spanish",
        "French",
        "Arabic",
        "Bengali",
        "Portuguese",
        "Russian",
        "Urdu",
        "Indonesian",
        "German",
        "Japanese",
        "Swahili",
        "Marathi",
        "Telugu",
        "Turkish",
        "Tamil",
        "Korean",
        "Vietnamese"
    ]

    df_driver['First Name'] = [
        "Liam","Noah","Oliver","Elijah","James","William","Benjamin","Lucas","Henry","Alexander",
        "Mason","Michael","Ethan","Daniel","Jacob","Logan","Jackson","Levi","Sebastian","Mateo",
        "Jack","Owen","Theodore","Aiden","Samuel","Joseph","John","David","Wyatt","Matthew",
        "Luke","Asher","Carter","Julian","Grayson","Leo","Jayden","Gabriel","Isaac","Lincoln",
        "Anthony","Hudson","Dylan","Ezra","Thomas","Charles","Christopher","Jaxon","Maverick","Josiah",
        "Isaiah","Andrew","Elias","Joshua","Nathan","Caleb","Ryan","Adrian","Miles","Eli",
        "Nolan","Christian","Aaron","Cameron","Ezekiel","Colton","Luca","Landon","Hunter","Jonathan",
        "Santiago","Axel","Easton","Cooper","Jeremiah","Angel","Roman","Connor","Jameson","Robert",
        "Greyson","Jordan","Ian","Carson","Jaxson","Leonardo","Nicholas","Dominic","Austin","Everett",
        "Brooks","Xavier","Kai","Jose","Parker","Adam","Jace","Wesley","Kayden","Silas",
        "Bennett","Declan","Waylon","Weston","Evan","Emmett","Micah","Ryder","Beau","Damian",
        "Brayden","Gael","Rowan","Harrison","Bryson","Sawyer","Amir","Kingston","Jason","Giovanni",
        "Vincent","Ayden","Chase","Myles","Diego","Nathaniel","Legend","Jonah","River","Tyler",
        "Cole","Braxton","George","Milo","Zachary","Ashton","Luis","Jasper","Kaiden","Adriel",
        "Gavin","Bentley","Calvin","Zion","Juan","Maxwell","Max","Ryker","Carlos","Emmanuel",
        "Jayce","Lorenzo","Ivan","Jude","August","Kevin","Malachi","Elliott","Rhett","Archer",
        "Karter","Arthur","Luka","Elliot","Thiago","Brandon","Camden","Justin","Jesus","Maddox",
        "King","Theo","Enzo","Matteo","Emiliano","Dean","Hayden","Finn","Brody","Antonio",
        "Abel","Alex","Tristan","Graham","Zayden","Judah","Xander","Miguel","Atlas","Messiah",
        "Barrett","Tucker","Timothy","Alan","Edward","Leon","Dawson","Eric","Ace","Victor",
        "Abraham","Nicolas","Jesse","Charlie","Patrick","Walker","Joel","Richard","Beckett","Blake",
        "Alejandro","Avery","Grant","Peter","Oscar","Matias","Amari","Lukas","Andres","Arlo",
        "Colt","Adonis","Kyrie","Steven","Felix","Preston","Marcus","Holden","Emilio","Remington",
        "Jeremy","Kaleb","Brantley","Bryce","Mark","Knox","Israel","Phoenix","Kobe","Nash",
        "Griffin","Caden","Kenneth","Kyler","Hayes","Jax","Rafael","Beckham","Javier","Maximus",
        "Simon","Paul","Omar","Kaden","Kash","Lane","Bryan","Riley","Zane","Louis",
        "Aidan","Paxton","Maximiliano","Karson","Cash","Cayden","Emerson","Tobias","Ronan","Brian",
        "Dallas","Bradley","Jorge","Walter","Josue","Khalil","Damien","Jett","Kairo","Zander",
        "Andre","Cohen","Crew","Hendrix","Colin","Chance","Malakai","Clayton","Daxton","Malcolm",
        "Lennox","Martin","Jaden","Kayson","Bodhi","Francisco","Cody","Erick","Kameron","Atticus",
        "Dante","Jensen","Cruz","Finley","Brady","Joaquin","Anderson","Gunner","Muhammad","Zayn",
        "Derek","Raymond","Kyle","Angelo","Reid","Spencer","Nico","Jaylen","Jake","Prince",
        "Manuel","Ali","Gideon","Stephen","Ellis","Orion","Rory","Cristian","Travis","Wade",
        "Warren","Fernando","Titus","Leonel","Edwin","Cairo","Corbin","Dakota","Ismael","Colson",
        "Killian","Major","Tanner","Apollo","Callum","Ricardo","Seth","Julius","Desmond","Kane",
        "Mario","Romeo","Cyrus","Kade","Iker","Dallas","Remy","Marshall","Lawson","Tyson",
        "Gage","Briggs","Sullivan","Donovan","Raiden","Zeke","Casey","Mathias","Ronin","Johnny",
        "Kendrick","Alonzo","Sterling","Raul","Taylor","Bruce","Mohamed","Royce","Solomon","Trevor",
        "Wilson","Felipe","Rome","Franklin","Noel","Alden","Kian","Jamison","Porter","Pierce",
        "Ruben","Raphael","Pedro","Saul","Troy","Caiden","Harvey","Devin","Conor","Marco",
        "Nehemiah","Andy","Cade","Reed","Quinn","Enrique","Alfredo","Brett","Rocco","Gavin",
        "Gunner","Leandro","Baylor","Kylan","Bo","Brayan","Cannon","Dennis","Drew","Mohammad",
        "Shawn","Dorian","Drake","Kasen","Gustavo","Kellen","Jase","Alessandro","Jaiden","Hector",
        "Cesar","Keegan","Rhys","Kieran","Lawrence","Malik","Trenton","Jalen","Curtis","Leonidas",
        "Trace","Wayne","Armani","Albert","Westin","Jamari","Erik","Emmitt","Soren","Alec",
        "Watson","Zaid","Cillian","Tate","Tony","Zayne","Corey","Bodie","Byron","Jared",
        "Gerardo","Jaime","Dexter","Pierce","Salem","Zachariah","Skye","Eduardo","Dominick","Quentin",
        "Tatum","Trent","Ray","Hugo","Damon","Malik","Moses","Callan","Kane","Koda",
        "Colby","Johan","Benson","Ariel","Alvaro","Ares","Koa","Jasiah","Darius","Gregor",
        "Sage","Shane","Mikael","Arjun","Braden","Eden","Kody","Ulises","Santos","Ayaan",
        "Legacy","Brock","Rylan","Marvin","Jabari","Makai","Ronald","Kylian","Ameer","Conrad",
        "Phillip","Bode","Rhodes","Gary","Zahir","Allan","Brixton","Elian","Dennis","Kole",
        "Kolton","Krew","Yusuf","Bruno","Axl","Case","Ronald","Rayan","Layton","Kylan",
        "Danny","Jaziel","Creed","Ibrahim","Rayan","Kristian","Armando","Zyaire","Jayson","Kyson",
        "Dillon","Madden","Esteban","Quincy","Callen","Harold","Alvin","Harlan","Kannon","Marcel",
        "Keaton","Morgan","Zaire","Gianni","Samson","Gunnar","Amos","Brendan","Sylas","Alden",
        "Duke","Stetson","Jayson","Eugene","Kaysen","Kenzo","Rayan","Mauricio","Augustus","Lucian",
        "Miller","Jamir","Marquis","Kasen","Camilo","Asa","Kashton","Otto","Royal","Talon",
        "Baker","Moshe","Karim","Scott","Frederick","Jair","Ricky","Aron","Bellamy","Emory",
        "Keanu","Leroy","Jamal","Mathew","Tripp","Morgan","Rex","Raylan","Benedict","Kellen"
    ]
    last_name_pool = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
    "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez",
    "Powell","Jenkins","Perry","Russell","Sullivan","Bell","Coleman","Butler","Henderson","Barnes",
    "Gonzales","Fisher","Vasquez","Simmons","Romero","Jordan","Patterson","Alexander","Hamilton","Graham",
    "Reynolds","Griffin","Wallace","Moreno","West","Cole","Hayes","Bryant","Herrera","Gibson",
    "Ellis","Tran","Medina","Aguilar","Stevens","Murray","Ford","Castro","Marshall","Owens",
    "Harrison","Fernandez","Mcdonald","Woods","Washington","Kennedy","Wells","Vargas","Henry","Chen",
    "Freeman","Webb","Tucker","Guzman","Burns","Crawford","Olson","Simpson","Porter","Hunter",
    "Gordon","Mendez","Silva","Shaw","Snyder","Mason","Dixon","Munoz","Hunt","Hicks",
    "Holmes","Palmer","Wagner","Black","Robertson","Boyd","Rose","Stone","Salazar","Fox",
    "Warren","Mills","Meyer","Rice","Schmidt","Garza","Daniels","Ferguson","Nichols","Stephens",
    "Soto","Weaver","Ryan","Gardner","Payne","Grant","Dunn","Kelley","Spencer","Hawkins",
    "Arnold","Pierce","Vazquez","Hansen","Peters","Santos","Hart","Bradley","Knight","Elliott",
    "Cunningham","Duncan","Armstrong","Hudson","Carroll","Lane","Riley","Andrews","Alvarado","Ray",
    "Delgado","Berry","Perkins","Hoffman","Johnston","Matthews","Pena","Richards","Contreras","Willis",
    "Carpenter","Lawrence","Sandoval","Guerrero","George","Chapman","Rios","Estrada","Ortega","Watkins"
    ]

    last_names = random.choices(last_name_pool, k=600)

    df_attractions = pd.read_csv('data_collection/Activities/oxford.csv')

    df_driver['Last Name'] = last_names   

    df_driver['City'] = [f'{driver_city}']*len(df_driver)

    types = ['Driver', 'Buddy', 'Driver-guide', 'BikeGuide']
    attract_codes = df_attractions['Activity / Attraction']
    df_driver = df_driver.reindex(columns=df_driver.columns.tolist() + types + attract_codes.tolist())

    languages_col = languages*3 + [0] * (600 - len(languages)*3)
    random.shuffle(languages_col)
    # print(languages_col)
    # print(len(languages_col))
    df_driver['Language0'] = ["English"] * len(df_driver)
    df_driver['Language1'] = languages_col
    random.shuffle(languages_col)
    df_driver['Language2'] = languages_col
    random.shuffle(languages_col)
    df_driver['Language3'] = languages_col

    df_driver['Driver'] = [1] * 150 + [0] * (600-150)
    df_driver['Buddy'] = [0] * 150 + [1] * (150) + [0] * (600-300)
    df_driver['Driver-guide'] = [0] * 300 + [1] * (150) + [0] * (600-450)
    df_driver['BikeGuide'] = [0] * 450 + [1] * (150)

    rating = [5]*200+[4]*100+[3]*100+[2]*100+[1]*100
    random.shuffle(rating)
    df_driver['Rating'] = rating
    print(df_attractions)

    generate_future_dates(df_driver=df_driver,busy_driver=20)

    for tick in attract_codes:
        value = df_attractions.loc[df_attractions["Activity / Attraction"] == tick,"Popularity"].iloc[0]   
        x = int(value*100)
        indicies = [1] * x + [0] * (600-x)
        random.shuffle(indicies)
        df_driver[f'{tick}'] = indicies


    print(df_driver.head())
    df_driver.to_csv('data_collection/Drivers/drivers01.csv')
    df_driver.to_csv('data_collection/Database/drivers01.csv')

    return 'data_collection/Drivers/drivers_oxford.csv'

def main():
    creat_drivers()

if __name__ == "__main__":
    main()




