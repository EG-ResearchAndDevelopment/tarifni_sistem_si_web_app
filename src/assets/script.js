let id_previous_month = 'jan'
let id_previous_day = 'pon'
let id_previous_blok = 'blok1'

window.onload = () => {
    setTimeout(() => {
        for (const element of ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'avg', 'sep', 'okt', 'nov', 'dec']) {
            addEventListeners(element, 'month')
        }
        for (const element of ['pon', 'tor', 'sre', 'cet', 'pet', 'sob', 'ned']) {
            addEventListeners(element, 'day')
        }
        for (const element of ['blok1', 'blok2', 'blok3', 'blok4', 'blok5', 'blok6', 'blok7']) {
            addEventListeners(element, 'blok')
        }
        console.log(document.getElementById('store'))
        
    }, 1500)
}

function addEventListeners(element, type) {
    if (type == 'month') {
        document.getElementById(element).addEventListener('click', function() {
            if (id_previous_month != element) {
                changeColor(element, 'month')
            }
        })
        document.getElementById(element).addEventListener('mouseenter', function() {
            if (id_previous_month != element) {
                hoverin(element, 'month')
            }
        })
        document.getElementById(element).addEventListener('mouseleave', function() {
            if (id_previous_month != element) {
                hoverout(element, 'month')
            }
        })
    } else if (type == 'day') {
        document.getElementById(element).addEventListener('click', function() {
            if (id_previous_day != element) {
                changeColor(element, 'day')
            }
        })
        document.getElementById(element).addEventListener('mouseenter', function() {
            if (id_previous_day != element) {
                hoverin(element, 'day')
            }
        })
        document.getElementById(element).addEventListener('mouseleave', function() {
            if (id_previous_day != element) {
                hoverout(element, 'day')
            }
        })
    } else if (type == 'blok') {
        document.getElementById(element).addEventListener('click', function() {
            if (id_previous_blok != element) {
                changeColor(element, 'blok')
            }
        })
        document.getElementById(element).addEventListener('mouseenter', function() {
            if (id_previous_blok != element) {
                hoverin(element, 'blok')
            }
        })
        document.getElementById(element).addEventListener('mouseleave', function() {
            if (id_previous_blok != element) {
                hoverout(element, 'blok')
            }
        })
    }
}

function changeColor(id_change, type) {
    document.getElementById(id_change).style.backgroundColor = '#C32025'
    document.getElementById(id_change + '-h5').style.color = '#ffffff'

    if (type == 'month') {
        if (id_previous_month == 'jan' || id_previous_month == 'feb' || id_previous_month == 'nov' || id_previous_month == 'dec') {
            document.getElementById(id_previous_month).style.backgroundColor = 'white'
            document.getElementById(id_previous_month + '-h5').style.color = '#C32025'
        } else {
            document.getElementById(id_previous_month).style.backgroundColor = 'white'
            document.getElementById(id_previous_month + '-h5').style.color = '#000000'
        }
        id_previous_month = id_change
    } else if (type == 'day') {
        if (id_previous_day == 'pon' || id_previous_day == 'tor' || id_previous_day == 'sre' || id_previous_day == 'cet' || id_previous_day == 'pet') {
            document.getElementById(id_previous_day).style.backgroundColor = 'white'
            document.getElementById(id_previous_day + '-h5').style.color = '#C32025'
        } else {
            document.getElementById(id_previous_day).style.backgroundColor = 'white'
            document.getElementById(id_previous_day + '-h5').style.color = '#000000'
        }
        id_previous_day = id_change
    } else if (type == 'blok') {
        document.getElementById(id_previous_blok).style.backgroundColor = 'white'
        document.getElementById(id_previous_blok + '-h5').style.color = '#000000'
        id_previous_blok = id_change
    }

    fadeOut();
}

function hoverin(element, type) {
    document.getElementById(element).style.backgroundColor = '#C32025'
    document.getElementById(element + '-h5').style.color = '#ffffff'
}

function hoverout(element, type) {
    if (type == 'month') {
        if (element == 'jan' || element == 'feb' || element == 'nov' || element == 'dec') {
            document.getElementById(element).style.backgroundColor = 'white'
            document.getElementById(element + '-h5').style.color = '#C32025'
        } else {
            document.getElementById(element).style.backgroundColor = 'white'
            document.getElementById(element + '-h5').style.color = '#000000'
        }
    } else if (type == 'day') {
        if (element == 'pon' || element == 'tor' || element == 'sre' || element == 'cet' || element == 'pet') {
            document.getElementById(element).style.backgroundColor = 'white'
            document.getElementById(element + '-h5').style.color = '#C32025'
        } else {
            document.getElementById(element).style.backgroundColor = 'white'
            document.getElementById(element + '-h5').style.color = '#000000'
        }
    } else if (type == 'blok') {
        document.getElementById(element).style.backgroundColor = 'white'
        document.getElementById(element + '-h5').style.color = '#000000'
    }
    
}

function fadeOut(){
	document.getElementById("blok-ura").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("blok-ura").style.opacity = 0;

    document.getElementById("cena").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("cena").style.opacity = 0;

    document.getElementById("cena-moc").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("cena-moc").style.opacity = 0;

    document.getElementById("predlagana-obr-moc").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("predlagana-obr-moc").style.opacity = 0;

    setTimeout(changePostavka, 100)
}

function fadeIn(){
	document.getElementById("blok-ura").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("blok-ura").style.opacity = 1;

    document.getElementById("cena").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("cena").style.opacity = 1;

    document.getElementById("cena-moc").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("cena-moc").style.opacity = 1;

    document.getElementById("predlagana-obr-moc").style.transition = "opacity 0.1s ease-in-out";
	document.getElementById("predlagana-obr-moc").style.opacity = 1;

    
}

function changePostavka() {
    let month = 'ostalo'
    let day = 'vikend'
    let blok = 'blok1'

    if (id_previous_month == 'jan' || id_previous_month == 'feb' || id_previous_month == 'nov' || id_previous_month == 'dec') {
        month = 'zima'
    }
    if (id_previous_day == 'pon' || id_previous_day == 'tor' || id_previous_day == 'sre' || id_previous_day == 'cet' || id_previous_day == 'pet') {
        day = 'delavnik'
    }

    if (month == 'ostalo' && day == 'vikend') {
        document.getElementById("blok1-slika").src = './assets/images/evri5.svg'
        document.getElementById("blok2-slika").src = './assets/images/evri4.svg'
        document.getElementById("blok3-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok4-slika").src = './assets/images/evri4.svg'
        document.getElementById("blok5-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok6-slika").src = './assets/images/evri4.svg'
        document.getElementById("blok7-slika").src = './assets/images/evri5.svg'


        switch (id_previous_blok) {
            case 'blok1':
                document.getElementById('blok-ura').innerHTML = '00:00 - 06:00'
                break;
            case 'blok2':
                document.getElementById('blok-ura').innerHTML = '06:00 - 07:00'
                break;
            case 'blok3':
                document.getElementById('blok-ura').innerHTML = '07:00 - 14:00'
                break;
            case 'blok4':
                document.getElementById('blok-ura').innerHTML = '14:00 - 16:00'
                break;
            case 'blok5':
                document.getElementById('blok-ura').innerHTML = '16:00 - 20:00'
                break;
            case 'blok6':
                document.getElementById('blok-ura').innerHTML = '20:00 - 22:00'
                break;
            case 'blok7':
                document.getElementById('blok-ura').innerHTML = '22:00 - 24:00'
                break;
        }
    }

    if (month == 'ostalo' && day == 'delavnik') {
        document.getElementById("blok1-slika").src = './assets/images/evri4.svg'
        document.getElementById("blok2-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok3-slika").src = './assets/images/evri2.svg'
        document.getElementById("blok4-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok5-slika").src = './assets/images/evri2.svg'
        document.getElementById("blok6-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok7-slika").src = './assets/images/evri4.svg'


        switch (id_previous_blok) {
            case 'blok1':
                document.getElementById('blok-ura').innerHTML = '00:00 - 06:00'
                break;
            case 'blok2':
                document.getElementById('blok-ura').innerHTML = '06:00 - 07:00'
                break;
            case 'blok3':
                document.getElementById('blok-ura').innerHTML = '07:00 - 14:00'
                break;
            case 'blok4':
                document.getElementById('blok-ura').innerHTML = '14:00 - 16:00'
                break;
            case 'blok5':
                document.getElementById('blok-ura').innerHTML = '16:00 - 20:00'
                break;
            case 'blok6':
                document.getElementById('blok-ura').innerHTML = '20:00 - 22:00'
                break;
            case 'blok7':
                document.getElementById('blok-ura').innerHTML = '22:00 - 24:00'
                break;
        }
    }

    if (month == 'zima' && day == 'vikend') {
        document.getElementById("blok1-slika").src = './assets/images/evri4.svg'
        document.getElementById("blok2-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok3-slika").src = './assets/images/evri2.svg'
        document.getElementById("blok4-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok5-slika").src = './assets/images/evri2.svg'
        document.getElementById("blok6-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok7-slika").src = './assets/images/evri4.svg'


        switch (id_previous_blok) {
            case 'blok1':
                document.getElementById('blok-ura').innerHTML = '00:00 - 06:00'
                break;
            case 'blok2':
                document.getElementById('blok-ura').innerHTML = '06:00 - 07:00'
                break;
            case 'blok3':
                document.getElementById('blok-ura').innerHTML = '07:00 - 14:00'
                break;
            case 'blok4':
                document.getElementById('blok-ura').innerHTML = '14:00 - 16:00'
                break;
            case 'blok5':
                document.getElementById('blok-ura').innerHTML = '16:00 - 20:00'
                break;
            case 'blok6':
                document.getElementById('blok-ura').innerHTML = '20:00 - 22:00'
                break;
            case 'blok7':
                document.getElementById('blok-ura').innerHTML = '22:00 - 24:00'
                break;
        }
    }

    if (month == 'zima' && day == 'delavnik') {
        document.getElementById("blok1-slika").src = './assets/images/evri3.svg'
        document.getElementById("blok2-slika").src = './assets/images/evri2.svg'
        document.getElementById("blok3-slika").src = './assets/images/evri1.svg'
        document.getElementById("blok4-slika").src = './assets/images/evri2.svg'
        document.getElementById("blok5-slika").src = './assets/images/evri1.svg'
        document.getElementById("blok6-slika").src = './assets/images/evri2.svg'
        document.getElementById("blok7-slika").src = './assets/images/evri3.svg'

        switch (id_previous_blok) {
            case 'blok1':
                document.getElementById('blok-ura').innerHTML = '00:00 - 06:00'
                break;
            case 'blok2':
                document.getElementById('blok-ura').innerHTML = '06:00 - 07:00'
                break;
            case 'blok3':
                document.getElementById('blok-ura').innerHTML = '07:00 - 14:00'
                break;
            case 'blok4':
                document.getElementById('blok-ura').innerHTML = '14:00 - 16:00'
                break;
            case 'blok5':
                document.getElementById('blok-ura').innerHTML = '16:00 - 20:00'
                break;
            case 'blok6':
                document.getElementById('blok-ura').innerHTML = '20:00 - 22:00'
                break;
            case 'blok7':
                document.getElementById('blok-ura').innerHTML = '22:00 - 24:00'
                break;
        }
    }
    setTimeout(fadeIn, 100)

}