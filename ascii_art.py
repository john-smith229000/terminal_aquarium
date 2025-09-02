from colorama import Fore

DECORATION_CATEGORIES = {
    'chest' : [Fore.YELLOW],
    'rock' : [Fore.WHITE, Fore.LIGHTBLACK_EX],
    'shell1' : [Fore.LIGHTCYAN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTWHITE_EX, Fore.WHITE, Fore.LIGHTBLACK_EX],
    'shell2' : [Fore.LIGHTMAGENTA_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTWHITE_EX, Fore.WHITE, Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX],
}

DECORATIONS = {
    'treasure' : {
        'closed': [
            ('chest', (
                '         __________',
                '        |\\_________\\',
                '        |\\|___}{___|',
                '        | |--------|',
                '        \\ |   ))   |',
                '         \\└--------┘',
            )),
        ],
        'open' : [
            ('chest',(
                '         _________',
                '        /\___}{___\\',
                '       | /       /',
                '        |\\O%O•*o^@\\',
                '       %| |-%------|',
                '     •%o\\ | % ))   |',
                '    .*%.•\\└--------┘',
            )),
        ],
    },
    'shells' : [
        ('shell1', (
            """            _--:":---_""",
            """          -\\  : | :  /-""", 
            """         (\\ : ' | ' : /)""",  
            """           \\ \\'.|.'/ /""",
            """             \\\\'|'//""", 
            """            {_`\\|/'_}""",

        )),
        ('shell2', (
            "     /\\",       
            "   /{`.}",      
            " _{;_`-._}",    
            "|  \\ `-./",     
            " \\_ \\ ./",      
            "   \\_|/",   
        )),
        ('shell2',(
            "       /\\",
            "      {.'}\\",
            "    {_.-'_;}_",
            "     \\.-' /  |",
            "      \\. / _/",
            "       \\|_/",
        )),
        ('shell1',(
'''               _.--"":""--._''',
"""             .' .-'.' '.'-. '.""",
"""            / .' /   '   \\ '. \\""",
"""           ;-.__.--:__:--.__.--;""",
"""           ;-.__.--.__.--.__.--;""",
"""            \\'. \\  :  :  / .' /""",
"""             '.\\ '. '. .' / .'""",
"""               `'--.:.:.--'`""",
        )),
    ],
}

CRAB = [
    (
    " _      _",
    "(<      >)",
    " `\,°°,/`",
    "//-\__/-\\\\",
    ),
    (
    " _      _",
    "(<      >)",
    " `\,°°,/`",
    "\\\\-\__/-//",
    ),
]

# Fish color sets - define what colors each fish type can have
FISH_COLOR_SETS = {
    'tropical_basic': [Fore.MAGENTA, Fore.YELLOW, Fore.BLUE, Fore.CYAN, Fore.RED, Fore.GREEN],
    'tropical_bright': [Fore.LIGHTCYAN_EX, Fore.LIGHTBLUE_EX, Fore.WHITE],
    'deep_sea': [Fore.BLUE, Fore.CYAN, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX],
    'goldfish': [Fore.YELLOW, Fore.LIGHTYELLOW_EX, Fore.RED],
    'angelfish': [Fore.WHITE, Fore.LIGHTCYAN_EX, Fore.CYAN],
    'exotic': [Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.RED],
    'common': [Fore.GREEN, Fore.BLUE, Fore.CYAN],
    'seahorse': [Fore.LIGHTYELLOW_EX, Fore.YELLOW, Fore.WHITE, Fore.LIGHTCYAN_EX, Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX],
    'marlin': [Fore.BLUE, Fore.CYAN, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX],
    'puffer': [Fore.YELLOW, Fore.LIGHTYELLOW_EX, Fore.WHITE],
    'blue_tang': {
        'body': [Fore.BLUE],
        'fin': [Fore.YELLOW, Fore.LIGHTGREEN_EX, Fore.LIGHTRED_EX, Fore.LIGHTYELLOW_EX],
    }
}

# Color adjustments for light mode (colors that don't show well on light backgrounds)
COLOR_ADJUSTMENTS = {
    'light_mode': {
        Fore.YELLOW: Fore.BLUE,           # Yellow hard to see on light cyan
        Fore.WHITE: Fore.LIGHTBLUE_EX,           # White invisible on light background
        Fore.CYAN: Fore.LIGHTBLACK_EX,
        Fore.LIGHTCYAN_EX: Fore.BLACK,     # Light cyan blends with background
        Fore.LIGHTYELLOW_EX: Fore.RED,    # Light yellow hard to see
        Fore.LIGHTBLUE_EX: Fore.BLUE,     # Light blue blends
        Fore.LIGHTMAGENTA_EX: Fore.MAGENTA, # Light magenta harder to see
    }
}

# Fish art styles - now supports both old string format and new multi-color format
FISH_ART_STYLES = {
    'single_line': {
        'forward': [
            ('tropical_basic', "><>"),
            ('tropical_basic', "><>"), 
            ('tropical_basic', "><>"),  # Multiple entries increase spawn chance
            ('deep_sea', ">-oO>"),
            ('deep_sea', ">-oO>"),
            ('goldfish', ">-oO>"),
            ('angelfish', "><(((°>"),
            ('exotic', "><(((°>"),
        ],
        'backward': [
            ('tropical_basic', "<><"),
            ('tropical_basic', "<><"),
            ('tropical_basic', "<><"),  # Multiple entries increase spawn chance
            ('deep_sea', "<Oo-<"),
            ('deep_sea', "<Oo-<"), 
            ('goldfish', "<Oo-<"),
            ('angelfish', "<°)))><"),
            ('exotic', "<°)))><"),
        ]
    },
    'multi_line_small': {
        'backward': [
            ('tropical_bright', (
                " /", 
                "/\\/", 
                "\\/\\", 
                " \\ "
                )),
            ('angelfish', (
                "   ,", 
                "  /|", 
                " /_/ ,", 
                "/o \\/|", 
                "\\<_/\\|", 
                " \\ \\ `", 
                "  \\|", 
                "   `"
                )),
            ('exotic', (
                "   ____", 
                "  /    \\", 
                " /----./", 
                "/ o    \\/|", 
                ">        |", 
                "\\ <)   /\\|", 
                " \\----'\\", 
                "  \\____/"
                )),
            ('common', (
                "  __////  /|",
                " / o   \\_/ |",
                "_> ))    _ <",
                "\\___+__/ \\ |",
                "    \\|    \\|"
                )),
            ('blue_tang', {
                'art' : [
                [('fin',"  __////  /|")],
                [('body', " / o   \\"),('fin',"_/ |")],
                [('body',"_> ))    _"),('fin'," <")],
                [('body',"\\___+__/"),('fin'," \\ |")],
                [('fin',"    \\|    \\|")],

                ],
                'color_keys':['body','fin']
                }),
        ],
        'forward': [
            ('tropical_bright', (
                " \\  ", 
                "\\/\\", 
                "/\\/", 
                " /  "
                )),
            ('angelfish', (
                "  ,",
                "  |\\",
                ", \\_\\",
                "|\\/ o\\",
                "|/\\_>/",
                "` / /",
                "  |/",
                "  `"
                )),
            ('exotic', (
                "   ____", 
                "  /    \\", 
                "  \\.----\\", 
                "|\\/    o \\", 
                "|        <", 
                "|/\\   (> /", 
                "  /'----/", 
                "  \\____/"
                )),
            ('common', (
                "|\\   \\\\\\\\__", 
                "| \\_/    o \\", 
                "> _    (( <_", 
                "| / \\__+___/", 
                "|/     |/"
                )),
            ('blue_tang', {
                'art' : [
                [('fin',"|\  \\\\\\\\__  ")],
                [('fin',"| \_"),('body',"/   o \\")],
                [('fin',"> "),('body',"_    (( <_")],
                [('fin',"| / "),('body',"\__+___/")],
                [('fin',"|/    |/    ")],
                ],
                'color_keys':['body','fin'],
                }),
        ],
    },
    'multi_line_large': {
        'backward': [
            ('exotic', (
                " ",
                "   ______/~/~/~/__           /((",
                " // __            ====__    /_((",
                "//  @))       ))))      ===/__((",
                "))           )))))))        __((",
                "\\\\     \)     ))))    __===\ _((",
                " \\\\_______________====      \_((",
                "                             \(("
            )),
            ('deep_sea', (
                '                ,"(',
                '               ////\                           _',
                '              (//////--,,,,,_____            ,"',
                '            _;"""----/////_______;,,        //',
                '''__________;"o,-------------......"""""`'-._/(''',
                '''      ""'==._.__,;;;;"""           ____,.-.==''',
                '             "-.:______,...;---""/"   "    \(',
                '''                 '-._      `-._("           \\\\''',
                "                     '-._                    '._"

            ))
        ],
        'forward': [
            ('exotic', (
                "                                 ",
                "))\\           __\\~\\~\\~\\______",
                "))_\\    __====            __ \\\\",
                "))__\\===      ((((       ((@  \\\\",
                "))__        (((((((           ))",
                "))_ /===__    ((((     (\\/    //",
                "))_/      ====_______________//",
                "))/"
            )),
            ('deep_sea', (
                '                             )",',
                '_                           /\\\\\\\\',
                ' ",            _____,,,,,--\\\\\\\\\\\\)',
                '  \\\\        ,,;_______\\\\\\\\\\----""";_',
                '''   )\\_.-`'"""""......-------------,o";__________''',
                '''   ==.-.,____           """;;;;,__._.==`""''',
                '   )/    "   "\\""---;...,______:.-"',
                '''  //           ")_.-'      _.-`''',
                '''_.`                    _.-`'''
            ))
        ],
    },
    'puffer': {
        'backward': [
            ('puffer', (
                ' __  _',
                '/. ^\\/',
                '>_"/',
            )),
            ('puffer', (
                ' ___   _',
                '/. ^^\\/-',
                '>__"/',
            )),
            ('puffer', (
                ' _.-._  _',
                '/ o ^^\\/_{',
                '>   {}/',
                ' `---`',
            )),
            ('puffer', (
                ''' _.^-._  _''',
                '''/ o ^ ^\\/_{''',
                '''> ^ {}^ /''',
                ''' `-__-'"''',
            )),
            ('puffer',(
                ''' _-^"‾‾"'^_  _-''',
                '''/ o  ^ ^ ^ \\/ {''',
                '''>   ^ { }^ ^|‾''',
                '''\\  ^ ^ ^ ^ /''',
                ''' `-,.__.-'‾''',
            )),
        ],
        'backward_swim': [
            ('puffer',(
                ''' _-^"‾‾"'^_''',
                '''/ o  ^ ^ ^ \\/‾‾{''',
                '''>   ^  { } ^|‾''',
                '''\\  ^ ^ ^ ^ /''',
                ''' `-,.__.-'‾''',
            )),
            ('puffer',(
                ''' _-^"‾‾"'^_  _-''',
                '''/ o  ^ ^ ^ \\/ {''',
                '''>   ^ { }^ ^|‾''',
                '''\\  ^ ^ ^ ^ /''',
                ''' `-,.__.-'‾''',
            )),
            ('puffer',(
                ''' _-^"‾‾"'^_''',
                '''/ o  ^ ^ ^ \\/‾‾{''',
                '''>   ^{ } ^ ^|‾''',
                '''\\  ^ ^ ^ ^ /''',
                ''' `-,.__.-'‾''',
            )),
            ('puffer',(
                ''' _-^"‾‾"'^_  _-''',
                '''/ o  ^ ^ ^ \\/ {''',
                '''>   ^ { }^ ^|‾''',
                '''\\  ^ ^ ^ ^ /''',
                ''' `-,.__.-'‾''',
            )),
        ],
        'forward': [
            ('puffer',(
                ' _  __ ',
                ' \/^ .\\',
                '   \\"_<',
            )),
            ('puffer',( 
                ' _   ___', 
                ' -\/^^ .\\',
                '    \\"__<',
            )),
            ('puffer',(
                '  _  _.-._',
                ' }_\\/^^ o \\',
                '    \\{}   <',
                "     '---'",
            )),
            ('puffer',(
                '''  _  _.-^._''', 
                ''' }_\\/^ ^ o \\''',
                '''   \\ ^{} ^ <''',
                """    "`-__-'""",
            )),
            ('puffer',(
                ''' -_  _^`"‾‾"^-_''' ,
                ''' } \\/ ^ ^ ^  o \\''',
                '''  ‾|^ ^{ } ^   <''',
                '''    \\ ^ ^ ^ ^  /''',
                """     ‾`-.__.,-'""" ,
            )),
        ],
            'forward_swim': [
                ('puffer',(
                '''     _^`"‾‾"^-_''',
                '''}‾‾\\/ ^ ^ ^  o \\''',
                ''' ‾ |^ { }  ^   <''',
                '''    \\ ^ ^ ^ ^  /''',
                """     ‾`-.__.,-'""" ,
                )),
                ('puffer',(
                ''' -_  _^`"‾‾"^-_''',
                ''' } \\/ ^ ^ ^  o \\''',
                '''  ‾|^ ^{ } ^   <''',
                '''    \\ ^ ^ ^ ^  /''',
                """     ‾`-.__.,-'""" ,
                )),
                ('puffer',(
                '''     _^`"‾‾"^-_''' ,
                '''}‾‾\\/ ^ ^ ^  o \\''',
                ''' ‾ |^ ^ { }^   <''',
                '''    \\ ^ ^ ^ ^  /''',
                """     ‾`-.__.,-'""" ,
                )),
                ('puffer',(
                ''' -_  _^`"‾‾"^-_''' ,
                ''' } \\/ ^ ^ ^  o \\''',
                '''  ‾|^ ^{ } ^   <''',
                '''    \\ ^ ^ ^ ^  /''',
                """     ‾`-.__.,-'""" ,
                )),

            ],
    },
    'seahorse': {
        'backward': [
            ('seahorse',(
                """     __.Cc_""",     
                """.-,__) o   )>""",  
                """``"=--._   .>""",  
                """        ) . \\.-`\\""",
                """       /__;  -- (""",
                """      (__ : /`._/""",
                """       \\__ (>""",    
                """       ,.\\  )>""",   
                """      ((_ / />""",   
                """       `-.-`""",  
            )),
            ('seahorse',(
                """     __.Cc_""",     
                """.-,__) o   )>""",  
                """``"=--._   .>""",  
                """        ) . \\.-\\""",
                """       /__;  --(""",
                """      (__ : /`./""",
                """       \\__ (>""",    
                """       ,.\\  )>""",   
                """      ((_ / />""",   
                """       `-.-`""",  
            )),
            ('seahorse',(
                """     __.Cc_""",     
                """.-,__) o   )>""",  
                """``"=--._   .>""",  
                """        ) . \\.\\""",
                """       /__;  -(""",
                """      (__ : /`/""",
                """       \\__ (>""",    
                """       ,.\\  )>""",   
                """      ((_ / />""",   
                """       `-.-`""",  
            )),
        ],
        'baby_backward': [
            ('seahorse',(
                """  _,""",
                """ /.\\""", 
                """' (<}""",
                """,_))'""",
                """ '"'""", 
            )),
            ('seahorse',(
                """  _,""",
                """ /.\\""", 
                """' (< }""",
                """,_))'""",
                """ '"'""", 
            )),
        ],
        'forward': [
            ('seahorse',(
                """      _cC.__""",
                """    <(   o (__,-.""" ,
                """    <.   _.--="''""",
                """/'-./ . (""",
                """) --  ;__\\""",
                """\\_.'\\ : __)""",
                """    <) __/""",
                """   <(  /.,""",
                """   <\\ \\ _))""",
                """     '-.-'""",

            )),
            ('seahorse',(
                """      _cC.__""",
                """    <(   o (__,-.""" ,
                """    <.   _.--="''""",
                """ /-./ . (""",
                """ )--  ;__\\""",
                """ \\.'\\ : __)""",
                """    <) __/""",
                """   <(  /.,""",
                """   <\\ \\ _))""",
                """     '-.-'""",
            )),
            ('seahorse',(
                """      _cC.__""",
                """    <(   o (__,-.""" ,
                """    <.   _.--="''""",
                """  /./ . (""",
                """  )-  ;__\\""",
                """  \\'\\ : __)""",
                """    <) __/""",
                """   <(  /.,""",
                """   <\\ \\ _))""",
                """     '-.-'""",

            )),
        ],
        'baby_forward': [
            ('seahorse',(
                """  ,_""",
                """  /.\\""",
                """{ >) `""",
                """ `((_,""",
                """ `"`""",
            )),
            ('seahorse',(
                """  ,_""",
                """  /.\\""",
                """ {>) `""",
                """ `((_,""",
                """ `"`""",
            )),
        ],
    },
}

BUBBLE_CHARS = ['.', '°', 'O', 'o','○']

SEAWEED_SEGMENTS = {
    'base_types': [("|||", Fore.GREEN), ("/|\\", Fore.GREEN), ("\\|/", Fore.GREEN)],
    'mid_types': [("|||", Fore.GREEN), ("|/|", Fore.GREEN), ("/|/", Fore.GREEN), ("|\\|", Fore.GREEN)],
    'top_types': [("~/~", Fore.GREEN), ("^|^", Fore.GREEN), ("~/\\", Fore.GREEN)]
}