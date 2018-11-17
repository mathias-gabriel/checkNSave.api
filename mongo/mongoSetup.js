let error = true

let res = [
    db.posts.drop(),
    db.posts.createIndex( { "geometry" : "2dsphere" } )
]

printjson(res)

if (error) {
    print('Error, exiting')
    quit(1)
}