function fillBase64(element) {

    const reader = new FileReader();
    reader.readAsDataURL(element.files[0]);

    reader.addEventListener("load", function () {

        document.getElementById("img-base64-txt").value = reader.result

    }, false);

}

function timeSince(date) {
    // time delta in seconds
    let seconds = Math.floor((new Date() - date) / 1000);

    let index = 0
    const units = ['year', 'month', 'day', 'hour', 'minute', 'second']
    const divisors = [31536000, 2592000, 86400, 3600, 60, 1]

    let interval = seconds / divisors[index]

    while (interval <= 1) {
        index ++ 
        interval = seconds / divisors[index]
    }

    // round down to integer value
    let value = Math.floor(interval)
    let unit = units[index]

    if (isNaN(value)) { value = 0 }
    if (unit == undefined) { unit = 'second'}

    // plural units
    if ( value > 1 ) { unit += 's' }

    return value + ' ' + unit

}

function formatAllDates() {
    let all_date_elements = document.getElementsByClassName("post-date")

    for (element of all_date_elements) {
        let date_string = element.innerHTML
        let post_date = Date.parse(date_string)
        element.innerHTML = "posted "+timeSince(post_date)+" ago"
    }
}

function mobileCheck() {
    let isMobile = document.getElementById("lets-go-mobile")

    var w = window.innerWidth;
    var h = window.innerHeight;
    
    // console.log(w/h + " " + isMobile.value)

    if (w/h < 0.75 && isMobile.value == 0) {
        // go mobile!

        let like_buttons = document.getElementsByClassName("like")
        let dislike_buttons = document.getElementsByClassName("dislike")
        let post_dates = document.getElementsByClassName("post-date")
        let post_scores = document.getElementsByClassName("post-score")

        for (like_button of like_buttons) {
            like_button.innerHTML = "👍" 
        }
        for (dislike_button of dislike_buttons) {
            dislike_button.innerHTML = "👎" 
        }
        for (post_date of post_dates) {
            post_date.innerHTML = post_date.innerHTML.slice(7, -4)
        }
        for (post_score of post_scores) {
            post_score.innerHTML = "🌻 "+post_score.innerHTML.slice(20)
        }

        isMobile.value = 1

    } else if (w/h > 0.75 && isMobile.value == 1) {
        // revert

        let like_buttons = document.getElementsByClassName("like")
        let dislike_buttons = document.getElementsByClassName("dislike")
        let post_dates = document.getElementsByClassName("post-date")
        let post_scores = document.getElementsByClassName("post-score")

        for (like_button of like_buttons) {
            like_button.innerHTML = "👍 Like"
        }
        for (dislike_button of dislike_buttons) {
            dislike_button.innerHTML = "👎 Dislike"
        }
        for (post_date of post_dates) {
            post_date.innerHTML = "posted "+post_date.innerHTML+" ago"
        }
        for (post_score of post_scores) {
            post_score.innerHTML = "sustainability score "+post_score.innerHTML.slice(2)
        }

        isMobile.value = 0
    }
}

if(window.addEventListener) {
    window.addEventListener('resize', mobileCheck, true);
}