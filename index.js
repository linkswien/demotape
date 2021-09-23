const youtubedl = require('youtube-dl-exec')

// Construct array with integers from 1 to 23
const districts = [...Array(24).keys()].slice(1)

const fetchStream = async (district) => {
    const paddedDistrict = String(district).padStart(2, 0)
    console.log(`[BV${paddedDistrict}] Try fetching stream`)
    await youtubedl(`https://stream.wien.gv.at/live/ngrp:bv${paddedDistrict}.stream_all/playlist.m3u8`, {
        printJson: true,
    })
        .then(output => console.log(`[BV${paddedDistrict}] Downloaded stream to ${output._filename}`))
        .catch(err => console.log(`[BV${paddedDistrict}] ${err.shortMessage}`))
        .finally(() => setTimeout(() => fetchStream(district), 20000))
}

districts.map((district, i) => {
    setTimeout(() => fetchStream(district), i * 500)
})
