# xVector 2D MMORPG Engine

This is an old hobby project where I played around with creating a simple 2D MMORPG engine written completely in Python.
I started this in my last semester of high school, and mainly tinkered with it over the next summer or two.
It was never finished since college started to take up more of my time, and since then my (very limited) free time has been spent
on a similar project in C++ with a more modern design.

To the best of my memory (which is not great, since I haven't touched this since 2013), this is the current state of the project 
as I left it:

- Client - Has a startup screen, login and registration forms, possibly some basic network connectivity with the server.  No
actual gameplay yet.
- Map editor - This is much more functional.  Multi-layered tilemaps can be saved and loaded, multiple tools are implemented,
multiple maps can be edited at the same time (MDI interface), and full undo/redo support.  No items, NPCs, or other entities
have been implemented.
- Server - Not entirely sure how much has been done here, but it's not a lot.  I believe I did some work with implementing an
asynchronous event loop to handle network events, and there appears to be a rudimentary Connection class that tracks state.
- Common Library - Some basic work on a network protocol has been done, and there is documentation to go along with it.

I'm not sure if I'll be working with this code again, since I have virtually no time for hobby projects anymore and I'm more
interested in working on the C++ engine instead.  Regardless, I've decided to release this code under the GPLv3 just because.
If you're interested in building your own 2D MMO, I would strongly recommend looking at a more complete solution if you want
fast results, or starting from scratch if you want to learn about the inner workings.  However, I realize that this code might
be interesting to someone as an example of... something, so here it is.

And yes, I was using Qt4 to handle the graphics.  I would not recommend that to anyone for performance reasons.  The new C++ engine
uses SFML and a whole lot of OpenGL shaders to achieve much better performance.
