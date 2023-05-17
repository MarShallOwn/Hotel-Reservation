from app import app

#dont forget to create volume using "docker volume create <volume name>"
# then run "docker run -p5000:5000 -v <volume-name>:/usr/src/app hotel-reservation:1.0"
if __name__ == '__main__':
    app.run()
    #app.run(debug=True)