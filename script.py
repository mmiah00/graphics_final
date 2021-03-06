import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========
  Checks the commands array for any animation commands
  (frames, basename, vary)
  Should set num_frames and basename if the frames
  or basename commands are present
  If vary is found, but frames is not, the entire
  program should exit.
  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    frameCheck = varyCheck = nameCheck = False
    name = ''
    num_frames = 1

    for command in commands:

        if command['op'] == 'frames':
            num_frames = int(command['args'][0])
            frameCheck = True
        elif command['op'] == 'vary':
            varyCheck = True
        elif command['op'] == 'basename':
            name = command['args'][0]
            nameCheck = True

    if varyCheck and not frameCheck:
        print('Error: Vary command found without setting number of frames!')
        exit()

    elif frameCheck and not nameCheck:
        print('Animation code present but basename was not set. Using "frame" as basename.')
        name = 'frame'

    return (name, num_frames)

"""======== second_pass( commands ) ==========
  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).
  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.
  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]

    for command in commands:
        if command['op'] == 'vary':
            args = command['args']
            knob_name = command['knob']
            start_frame = args[0]
            end_frame = args[1]
            start_value = float(args[2])
            end_value = float(args[3])
            value = 0

            if ((start_frame < 0) or
                (end_frame >= num_frames) or
                (end_frame <= start_frame)):
                print('Invalid vary command for knob: ' + knob_name)
                exit()

            delta = (end_value - start_value) / (end_frame - start_frame)

            for f in range(num_frames):
                if f == start_frame:
                    value = start_value
                    frames[f][knob_name] = value
                elif f >= start_frame and f <= end_frame:
                    value = start_value + delta * (f - start_frame)
                    frames[f][knob_name] = value
                #print 'knob: ' + knob_name + '\tvalue: ' + str(frames[f][knob_name])
    return frames

def mesh_parser (file, symbols):
    l = open (file, "r").read ()
    lines = l.split ("\n")

    commands = ['v', 'vt', 'vp', 'f', 'l', 'mtllib', 'usemtl', 'o', 'g', 'd', 'Tr', 's']
    vertices = []
    faces = {} #key = group name and value = list of faces {group1: [f1, f2, f3, f4]}
    mttlib = {} #key = constant and value = values of ka, kd, ks
    usemtl = {} #key = group name and value = list w specs {group1 : [blueteal, {ka : 0, kd : 0, ks : 0, illum : 0, ns : 0}]}
    group_now = None

    file_commands = {}
    for command in lines:
        c = command.split (" ")
        if c[0] in commands:
            while '' in c:
                c.remove ('')
            if c[0] == 'g':
                if len (c) > 1:
                    group_now = c[1]
                else:
                    group_now = "group1"
                faces[group_now] = []
            if c[0] == 'v':
                vertices.append ([float (c[1]), float (c[2]), float (c[3])])
            if c[0] == 'f':
                adding = c[1:]
                faces[group_now].append ([int (x) - 1 for x in adding]) #subtracting one so it aligns with the indices in the vertices list
            if c[0] == 'mtllib': #using a .mtl file
                s = open (c[1],'r').read ()
                specs = s.split ("\n\n")
                mtl_now = None
                for info in specs:
                    k = info.split ("\n")
                    for line in k:
                        if line != '':
                            line = line.split (" ")
                            if line[0] == 'newmtl':
                                mtl_now = line[1]
                                mttlib[mtl_now] = {}
                            elif line[0] != '#newmtl':
                                mttlib[mtl_now][line[0]] = [float (x) for x in line[1:]]
            if c[0] == 'usemtl':
                if c[1] in mttlib.keys ():
                    usemtl[group_now] = c[1]
                    symbols[c[1]] = ['constants', {'red' : [],
                                                      'green' : [],
                                                      'blue' : []}]
                    if 'Ka' not in mttlib[c[1]]:
                        symbols[c[1]][1]['red'].append (0.0)
                        symbols[c[1]][1]['green'].append (0.0)
                        symbols[c[1]][1]['blue'].append (0.0)
                    else:
                        ambient = mttlib[c[1]]['Ka']
                        symbols[c[1]][1]['red'].append (ambient[0])
                        symbols[c[1]][1]['green'].append (ambient[1])
                        symbols[c[1]][1]['blue'].append (ambient[2])

                    if 'Kd' not in mttlib[c[1]]:
                        symbols[c[1]][1]['red'].append (0.0)
                        symbols[c[1]][1]['green'].append (0.0)
                        symbols[c[1]][1]['blue'].append (0.0)
                    else:
                        diffuse = mttlib[c[1]]['Kd']
                        symbols[c[1]][1]['red'].append (diffuse[0])
                        symbols[c[1]][1]['green'].append (diffuse[1])
                        symbols[c[1]][1]['blue'].append (diffuse[2])

                    if 'Ks' not in mttlib[c[1]]:
                        symbols[c[1]][1]['red'].append (0.0)
                        symbols[c[1]][1]['green'].append (0.0)
                        symbols[c[1]][1]['blue'].append (0.0)
                    else:
                        specular = mttlib[c[1]]['Ks']
                        symbols[c[1]][1]['red'].append (specular[0])
                        symbols[c[1]][1]['green'].append (specular[1])
                        symbols[c[1]][1]['blue'].append (specular[2])
            #file_commands.append (c)
    file_commands['vertices'] = vertices
    file_commands['faces'] = faces
    file_commands['constants'] = usemtl
    return file_commands

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[[0.5,
              0.75,
              1],
             [255,
              255,
              255]]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'
    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    knoblists = {} #saves all the knob lists (key = name and value = list of values for all the knobs)
    for f in range(num_frames):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []


        #Set symbol values for multiple frames
        if num_frames > 1:
            frame = frames[f]
            for knob in frame:
                symbols[knob][1] = frame[knob]
                #print('\tkob: ' + knob + '\tvalue: ' + str(frame[knob]))

        for command in commands:
            #print(command)
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                #print ("making box\t\t lights: ", len (lights))
                if command['constants']:
                    reflect = command['constants']
                #print (command['cs'])
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                if command['cs']:
                    # print ("CS: ", command['cs'])
                    # print (symbols[command['cs']][1])
                    matrix_mult(symbols[command['cs']][1], tmp )
                else:
                    #print ("CS: ", 'DEFAULT')
                    matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                #print ("making sphere\t\t lights: ", len (lights))
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp, args[0], args[1], args[2], args[3], step_3d)
                if command['cs']:
                    matrix_mult(symbols[command['cs']][1], tmp )
                else:
                    #print ("CS: ", 'DEFAULT')
                    matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                #print ("making torus\t\t lights: ", len (lights))
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp, args[0], args[1], args[2], args[3], args[4], step_3d)
                if command['cs']:
                    # print ("CS: ", command['cs'])
                    # print (symbols[command['cs']][1])
                    matrix_mult(symbols[command['cs']][1], tmp )
                else:
                    #print ("CS: ", 'DEFAULT')
                    matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                if command['knob']:
                    knob_value = symbols[command['knob']][1]
                tmp = make_translate(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if command['knob']:
                    knob_value = symbols[command['knob']][1]
                tmp = make_scale(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if command['knob']:
                    knob_value = symbols[command['knob']][1]
                theta = args[1] * (math.pi/180) * knob_value
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            ######################### ADDITIONS #########################
            elif c == 'save_coord_system': #saving the top of the coordinates stack
                n = command['cs']
                copee = [x[:] for x in stack[-1]]
                symbols[n][1] = copee
                # print ("saving coordinate system ", name)
                # print (symbols[name])
            elif c == 'set': #sets a knob's value
                name = command['knob']
                symbols[name][1] = command['args'][0]
                #print (symbols)
            elif c == 'setknobs': #sets all the knobs' value
                for symb in symbols:
                    if symbols[symb][0] == 'knob':
                        symbols[symb][1] = command['args'][0]
                    #print (symb, " : ", symbols[symb][1])
            elif c == 'save_knobs':
                name = command['args']
                knoblists[name] = []
                for knob in all_knobs:
                    val = all_knobs[knob]
                    knoblists[name].append (val)
            elif c == 'light':
                lite = symbols[command['light']][1]
                light.append ([lite['location'], lite['color']])
            elif c == 'mesh':
                #print (command)
                parsed_file = mesh_parser (command['args'][0] + ".obj", symbols)
                for group in parsed_file['faces']:
                    if len (parsed_file['faces'][group]) > 3:
                        add_mesh (tmp, parsed_file, group)
                        if command['cs']:
                            matrix_mult (symbols[command['cs']][1], tmp)
                        else:
                            matrix_mult (stack[-1], tmp)
                        try:
                            if command['constants']:
                                reflect = command['constants']
                            else:
                                reflect = parsed_file['constants'][group]
                        except:
                            if command['constants']:
                                reflect = command['constants']
                        draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                        tmp = []
                        reflect = '.white'

            #############################################################
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            # end operation loop
        if num_frames > 1:
            fname = 'anim/%s%03d.png'%(name, f)
            print('Saving frame: '  + fname)
            save_extension(screen, fname)
        # end frames loop
    if num_frames > 1:
        make_animation(name)
