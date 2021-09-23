const youtubedl = require('youtube-dl-exec')

// Construct array with integers from 1 to 23
const districts = [...Array(24).keys()].slice(1)

const fetchStream = async (district) => {
    console.log(`Try fetching stream from ${district}`)
    await youtubedl(`https://stream.wien.gv.at/live/ngrp:bv${String(district).padStart(2, 0)}.stream_all/playlist.m3u8`, {
        printJson: true,
    })
        .then(output => console.log(output))
        .catch(err => console.log(err.shortMessage))
        .finally(() => setTimeout(() => fetchStream(district), 20000))
}

districts.map(district => {
    fetchStream(district)
})
