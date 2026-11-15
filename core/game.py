"""Application controller: UI scenes share one deterministic mission state."""
import textwrap
from ursina import *
from systems.engineering import *
from systems.mission import Mission
from core.save_manager import SaveManager,DEFAULT_SETTINGS
from objects.world import World
from audio.manager import AudioManager
from ui.widgets import label,panel,button,Bar,CYAN,WHITE,MUTED,ORANGE

def wrap(text,width=42):return '\n'.join(textwrap.wrap(text,width))
class Game(Entity):
    def __init__(self):
        super().__init__();self.store=SaveManager();self.saved=self.store.load();self.settings=self.saved['settings']
        self.audio=AudioManager(self.settings);self.world=World();self.world.stars.enabled=not self.settings['low_graphics'];self.ui=None;self.screen='';self.category='solar'
        self.design=default_design();self.config=dict(launchers=1,transfers=0,orbits=0);self.mission=None
        self.history=self.saved['history'];self.best=self.saved['best'];self.clock=0;self.ui_tick=0;self.auto_save=0;self.last_phase='';self.last_message=''
        self.review_page=0;self.return_screen='menu';self.show('menu')
    def btn(self,text,x,y,callback,w=.3,accent=False):
        return button(self.ui,text,x,y,callback,w,accent,self.audio)
    def txt(self,text,x,y,scale=1,c=WHITE):return label(self.ui,text,x,y,scale,c)
    def header(self,section,title,subtitle=''):
        self.txt('M / A     MISSION ARCHITECT',-.83,.465,.75,CYAN)
        self.txt(section.upper(),.40,.465,.7,MUTED)
        self.txt(title,-.79,.385,1.65)
        if subtitle:self.txt(subtitle,-.79,.33,.78,MUTED)
        Entity(parent=self.ui,model='quad',position=(0,.425,0),scale=(1.66,.001),color=color.rgb32(35,65,84))
    def show(self,name):
        if self.ui:destroy(self.ui)
        self.ui=Entity(parent=camera.ui);self.screen=name
        if not self.settings['reduced_motion']:
            self.ui.y=-.012;self.ui.animate_y(0,duration=.16)
        self.world.setup({'menu':'menu','briefing':'briefing','designer':'designer','planning':'planning','trajectory':'planning','review':'designer','simulation':'simulation'}.get(name,'menu'),self.design,self.config)
        getattr(self,'screen_'+name)()
        self.fit_ui()
    def fit_ui(self):
        factor=min(1,camera.aspect_ratio/(16/9))
        self.ui.scale=factor
        for b in self.ui.children:
            if isinstance(b,Button):b.text_size=.8*factor;b.highlight_text_size=.8*factor
        self.last_aspect=camera.aspect_ratio
    def persist(self):
        data=dict(version=1,settings=self.settings,mission=self.mission.to_dict() if self.mission else self.saved.get('mission'),history=self.history[-10:],best=self.best)
        ok=self.store.save(data)
        if ok:self.saved=data
        elif self.screen=='simulation':self.mission.message='Save could not be written. Mission remains playable in this session.'
        return ok
    def new(self):
        self.mission=None;self.saved['mission']=None;self.design=default_design();self.config=dict(launchers=1,transfers=0,orbits=0);self.show('briefing')
    def resume(self):
        self.mission=Mission(**self.saved['mission']);self.design=self.mission.design.copy();self.config=self.mission.config.copy();self.mission.paused=False
        self.show('results' if self.mission.phase=='Results' else 'simulation')
    def screen_menu(self):
        self.txt('INDEPENDENT EXPLORATION PROGRAM  /  01',-.77,.38,.75,CYAN)
        self.txt('MARS',-.79,.25,4.8)
        self.txt('MISSION ARCHITECT',-.77,.105,1.6)
        self.txt('Design. Explore. Discover.',-.77,.035,1.05,MUTED)
        self.btn('START MISSION',-.59,-.07,self.new,.36,True)
        y=-.135
        if self.saved.get('mission'):
            self.btn('CONTINUE MISSION',-.59,y,self.resume,.36);y-=.06
        self.btn('MISSION GUIDE',-.59,y,lambda:self.show('guide'),.36);y-=.06
        self.btn('SETTINGS',-.59,y,lambda:self.open_settings('menu'),.36);y-=.06
        self.btn('CREDITS',-.59,y,lambda:self.show('credits'),.36);y-=.06
        self.btn('EXIT',-.59,y,self.quit,.36)
        self.txt(f'BEST MISSION  {self.best:02d} / 100',.37,-.36,.85,CYAN)
        self.txt('A game about the decisions that get us there.',.12,-.41,.72,MUTED)
        self.txt('SPACE MISSION DESIGN CHALLENGE  /  2026',-.78,-.46,.65,MUTED)
    def screen_briefing(self):
        self.header('01 / Briefing','Operation Mars Mapper','An orbiter. Five regions. One carefully balanced mission.')
        panel(self.ui,-.49,-.035,.61,.64)
        self.txt('WHY WE GO',-.76,.24,.85,CYAN)
        self.txt(wrap('Mars preserves evidence of ancient rivers and lakes. Orbital images help scientists study those environments and assess terrain for future exploration.',47),-.76,.19,.9)
        self.txt('MISSION CONTRACT',-.76,.035,.85,CYAN)
        self.txt('01  Reach Mars orbit\n02  Map all five assigned regions\n03  Reach 80% coverage in each region\n04  Return at least 80% of collected data\n05  Keep the spacecraft operational',-.76,-.02,.86)
        self.txt('260 M credits total budget\n24 simulated hours of orbital operations\nTypical play time: 10-20 minutes',-.76,-.19,.82,MUTED)
        self.txt('EARTH  >  TRANSFER  >  MARS',.02,-.23,.9,CYAN)
        self.txt('Illustrative distances and planet sizes.\nTransfer reference: about 259 days.',.02,-.29,.78,MUTED)
        self.btn('BACK',-.64,-.42,lambda:self.show('menu'),.24)
        self.btn('DESIGN SPACECRAFT  >',.56,-.42,lambda:self.show('designer'),.44,True)
    def change_part(self,index):
        self.design[self.category]=index;self.audio.play('deploy');self.show('designer')
    def screen_designer(self):
        self.header('02 / Engineering','Build your orbiter','Select a system, compare its trade-offs, then inspect the live model.')
        panel(self.ui,-.63,-.015,.40,.61);panel(self.ui,.60,-.015,.46,.61)
        for i,k in enumerate(COMPONENTS):
            def choose(key=k):self.category=key;self.show('designer')
            self.btn(k.upper(),-.63,.24-i*.058,choose,.35,k==self.category)
        self.txt(self.category.upper(),.40,.265,.85,CYAN)
        for i,p in enumerate(COMPONENTS[self.category]):
            self.btn(('> ' if self.design[self.category]==i else '')+p['name'],.60,.20-i*.061,lambda n=i:self.change_part(n),.39,self.design[self.category]==i)
        p=parts(self.design)[self.category]
        self.txt(wrap(p['description'],32),.40,-.005,.82)
        self.txt(f"{p['mass']} kg  /  {p['cost']} M credits\nOperating load: {p['power']} W",.40,-.105,.78,MUTED)
        performance='  /  '.join(f'{k}: {v}' for k,v in p.items() if k not in ('id','name','mass','cost','power','description'))
        self.txt(wrap(performance,32),.40,-.18,.72,CYAN)
        self.txt('Right-drag: rotate   |   Wheel: zoom   |   R: reset',-.32,-.275,.67,MUTED)
        self.design_dashboard()
        self.btn('BRIEFING',-.66,-.445,lambda:self.show('briefing'),.24)
        self.btn('PLAN MISSION  >',.63,-.445,lambda:self.show('planning'),.33,True)
    def design_dashboard(self):
        s=stats(self.design,self.config);panel(self.ui,0,-.365,1.66,.11)
        items=[('WET MASS',f"{s['mass']:.0f} kg"),('TOTAL COST',f"{s['cost']:.0f} / 260 M"),('MARS SOLAR',f"{s['generation']:.0f} W"),('PEAK LOAD',f"{s['peak']:.0f} W"),('BATTERY',f"{s['battery']:.0f} Wh"),('DELTA-V',f"{s['dv']:.0f} m/s")]
        for i,(k,v) in enumerate(items):
            x=-.79+i*.275;self.txt(k,x,-.325,.62,MUTED);self.txt(v,x,-.36,.88,CYAN)
    def change_plan(self,key,index):self.config[key]=index;self.show('planning')
    def screen_planning(self):
        self.header('03 / Trajectory','Choose your route','The launcher supplies Earth escape. The orbiter must pay for Mars capture.')
        for col,key in enumerate(('launchers','transfers','orbits')):
            x=-.55+col*.55;panel(self.ui,x,-.03,.52,.64)
            self.txt(key.upper(),x-.23,.26,.85,CYAN)
            for i,opt in enumerate(MISSION[key]):
                self.btn(('> ' if self.config[key]==i else '')+opt['name'],x,.20-i*.065,lambda k=key,n=i:self.change_plan(k,n),.46,self.config[key]==i)
            opt=MISSION[key][self.config[key]]
            self.txt(wrap(opt['description'],36),x-.23,-.015,.8)
            if key=='launchers':s=f"{opt['capacity']} kg at C3 {opt['c3']} km2/s2\nLaunch cost: {opt['cost']} M credits"
            elif key=='transfers':s=f"Cruise: {opt['days']} days\nC3 required: {opt['c3']} km2/s2\nMars excess speed: {opt['vinf']} km/s"
            else:s=f"Altitude: {opt['peri']} x {opt['apo']} km\nPeriod: {orbit_period(opt)/60:.0f} min\nCapture + correction:\n{capture_dv(opt,plans(self.config)[1]):.0f} m/s"
            self.txt(s,x-.23,-.19,.78,CYAN)
        self.btn('< DESIGN',-.65,-.42,lambda:self.show('designer'),.28)
        self.btn('VIEW TRANSFER',0,-.42,lambda:self.show('trajectory'),.31)
        self.btn('READINESS REVIEW  >',.58,-.42,lambda:self.show('review'),.43,True)
    def screen_trajectory(self):
        self.header('03 / Transfer geometry','Earth to Mars','Circular coplanar reference; sizes and distances are exaggerated for clarity.')
        l,t,o=plans(self.config)
        panel(self.ui,-.59,-.06,.43,.49)
        self.txt('MISSION ROUTE',-.77,.15,.86,CYAN)
        self.txt(wrap(t['name'],28)+f"\n\n{t['days']} days cruise\nC3: {t['c3']} km2/s2\nArrival excess: {t['vinf']} km/s\n\n"+wrap('Cyan: reference transfer ellipse. Blue: Earth orbit. Orange: Mars orbit. Gold sphere: Sun.',30),-.77,.09,.8)
        self.txt('Start at Earth orbit. Arrive where Mars will be.',-.20,-.29,.81,CYAN)
        self.txt('Fast and off-window options use illustrative energy budgets;\nthe curve shows the Hohmann reference, not their computed paths.',-.20,-.34,.70,MUTED)
        self.btn('BACK TO PLANNING',-.56,-.43,lambda:self.show('planning'),.43)
    def screen_review(self):
        self.header('04 / Readiness','Flight readiness review','Hard constraints block launch; warnings let you test the consequences.')
        panel(self.ui,0,-.035,1.60,.65);s=stats(self.design,self.config);errors,warnings=review(self.design,self.config)
        self.txt('SPACECRAFT MANIFEST',-.75,.25,.85,CYAN)
        for i,(k,p) in enumerate(parts(self.design).items()):self.txt(f"{k.title():12}  {p['name']}",-.75,.20-i*.046,.77)
        self.txt(f"Mass {s['mass']:.0f} kg  |  Cost {s['cost']:.0f} M\nSolar {s['generation']:.0f} W / peak {s['peak']:.0f} W\nDelta-v {s['dv']:.0f} / required {s['required']:.0f} m/s\nStorage {s['storage']:.0f} MB / radio {s['rate']} Mbps\nImage resolution {s['resolution']:.1f} m/pixel",.02,.24,.87)
        notes=errors+warnings or ['READY: mass, budget, power and propulsion checks passed.']
        start=(self.review_page % max(1,(len(notes)+2)//3))*3
        self.txt('\n\n'.join(wrap(x,54) for x in notes[start:start+3]),.02,.065,.75,ORANGE if errors or warnings else CYAN)
        if len(notes)>3:self.btn('MORE CHECKS  >',.40,-.255,self.next_checks,.36)
        self.txt(' / '.join(x['name'] for x in plans(self.config)),-.75,-.30,.75,MUTED)
        self.btn('< REVISE',-.65,-.42,lambda:self.show('designer'),.28)
        self.btn('FIX BLOCKERS' if errors else 'BEGIN MISSION  >',.57,-.42,(lambda:self.show('planning')) if errors else self.launch,.43,not errors)
    def next_checks(self):self.review_page+=1;self.show('review')
    def launch(self):
        if review(self.design,self.config)[0]:return
        self.mission=Mission(self.design.copy(),self.config.copy());self.last_phase='';self.last_message='';self.persist();self.show('simulation');self.audio.play('launch')
    def screen_simulation(self):
        self.header('05 / Mission control','Operation Mars Mapper')
        panel(self.ui,-.63,-.025,.4,.65);panel(self.ui,.65,-.025,.36,.65)
        self.phase_label=self.txt('',-.79,.29,.83,CYAN)
        self.telemetry=self.txt('',-.79,.235,.78)
        self.power_text=self.txt('',-.79,.035,.77)
        self.power_bar=Bar(self.ui,-.79,-.055,.31)
        self.storage_text=self.txt('',-.79,-.10,.77)
        self.data_bar=Bar(self.ui,-.79,-.18,.31)
        self.other_text=self.txt('',-.79,-.215,.77)
        self.target_buttons=[]
        self.txt('SCIENCE REGIONS',.50,.28,.78,CYAN)
        for i,t in enumerate(TARGETS):
            self.target_buttons.append(self.btn(t['name'],.65,.215-i*.056,lambda n=i:self.select_target(n),.30))
        self.target_info=self.txt('',.50,-.09,.72,MUTED)
        self.btn('CAMERA  [I]',.65,-.235,self.toggle_image,.30)
        self.btn('DOWNLINK  [T]',.65,-.295,self.toggle_radio,.30)
        self.status=self.txt('',-.40,-.25,.80,CYAN)
        self.notice=self.txt('',-.78,-.37,.82)
        self.btn('PAUSE / RESUME',-.64,-.445,self.pause,.31)
        self.speed_button=self.btn('SPEED  1x',-.29,-.445,self.speed,.28)
        self.btn('VIEW',.01,-.445,self.next_view,.22)
        self.btn('SAVE & MENU',.31,-.445,self.save_menu,.30)
        self.btn('END MISSION',.65,-.445,self.end_dialog,.30)
        self.refresh_telemetry()
    def select_target(self,i):
        self.mission.select(i);self.audio.play('click');self.refresh_telemetry()
    def toggle_image(self):
        if self.mission.phase=='Mapping':self.mission.toggle_image();self.audio.play('click')
        else:self.mission.message='Camera becomes available after Mars orbit insertion.'
    def toggle_radio(self):
        if self.mission.phase=='Mapping':self.mission.toggle_radio();self.audio.play('data')
        else:self.mission.message='Science downlink begins after orbital observations.'
    def pause(self):self.mission.paused=not self.mission.paused
    def speed(self):
        self.mission.speed={1:4,4:12,12:1}[self.mission.speed];self.speed_button.text=f'SPEED  {self.mission.speed}x'
    def next_view(self):self.world.view=self.world.view%3+1
    def save_menu(self):self.persist();self.show('menu')
    def end_dialog(self):
        self.mission.paused=True;self.show('confirm_end')
    def screen_confirm_end(self):
        self.header('Mission paused','End this mission?')
        panel(self.ui,0,0,1.2,.34)
        self.txt('Review the science and resources collected so far.\nYou can redesign and retry from the results screen.',-.5,.09,.95)
        self.btn('KEEP FLYING',-.28,-.1,self.keep_flying,.35,True)
        self.btn('END & REVIEW',.28,-.1,self.end_mission,.35)
    def keep_flying(self):self.mission.paused=False;self.show('simulation')
    def end_mission(self):self.mission.finish('Mission ended by director. Review incomplete targets and data return.');self.record_result()
    def refresh_telemetry(self):
        m=self.mission;s=m.s
        self.phase_label.text=('PAUSED / ' if m.paused else '')+m.phase.upper()
        day=plans(m.config)[1]['days']*(min(1,m.phase_time/18) if m.phase=='Cruise' else (1 if m.phase in ('Mars arrival','Mapping','Results') else 0))
        self.telemetry.text=(f"CRUISE DAY  {day:.0f}\nOPS TIME  {m.ops_seconds/3600:.2f} / 24 h\nHEALTH  {m.health:.0f}%\nPROPELLANT  {m.fuel:.1f} kg")
        self.power_text.text=f"SOLAR {m.generated_power:.0f} W / LOAD {m.load:.0f} W\nBATTERY  {m.battery:.0f} / {s['battery']} Wh"
        self.storage_text.text=f"STORED  {m.stored:.0f} / {s['storage']} MB\nRETURNED  {m.fraction*100:.1f}%"
        self.other_text.text=f"THERMAL  {m.temperature:.1f} C\nORBIT  {s['period']/60:.0f} min"
        self.power_bar.set(m.battery/s['battery']);self.data_bar.set(m.stored/s['storage'])
        for i,b in enumerate(self.target_buttons):
            b.text=f"{'>' if i==m.selected else ' '} {TARGETS[i]['name']}  {m.coverage[i]:.0f}%"
            b.color=color.rgb32(20,66,89) if i==m.selected else color.rgb32(16,35,53)
        t=TARGETS[m.selected]
        self.target_info.text=f"{t['lat']:+.2f} lat / {t['lon']:.2f} E\n"+wrap(t['reason'],27)
        if m.phase=='Mapping':
            self.status.text=f"{'ECLIPSE' if m.eclipse else 'SUNLIT'}   /   {'EARTH LINK OPEN' if m.link else 'EARTH OCCULTED'}\nCAMERA {'ARMED' if m.imaging else 'OFF'}   /   RADIO {'ARMED' if m.transmitting else 'OFF'}\n{'DUST INTERFERENCE' if m.dusty else 'CLEAR'}   /   {'TARGET PASS' if m.opportunity else 'WAITING FOR PASS'}"
        else:self.status.text={'Launch':f"LAUNCH  T {m.phase_time-3:+.1f} s",'Earth departure':'ARRAY DEPLOYMENT / SYSTEMS ONLINE','Cruise':'INTERPLANETARY COAST / TIME COMPRESSED','Mars arrival':'MARS ORBIT INSERTION / ENGINE FIRING'}.get(m.phase,'')
        self.notice.text=wrap(m.message,110);self.speed_button.text=f'SPEED  {m.speed}x'
    def record_result(self):
        r=self.mission.result();self.history.append(r);self.best=max(self.best,r['score']);self.persist();self.audio.play('success' if r['success'] else 'failure');self.show('results')
    def screen_results(self):
        m=self.mission;r=m.result();self.header('06 / Mission report','Mission accomplished' if r['success'] else 'Mission debrief','Every outcome is an engineering lesson. Refine the design and fly again.')
        panel(self.ui,0,-.025,1.60,.64)
        self.txt(f"{r['score']:02d}",-.74,.25,4,CYAN);self.txt('/ 100',-.51,.17,1,MUTED)
        self.txt('SCIENCE RETURN',-.74,.055,.8,CYAN)
        for i,t in enumerate(TARGETS):self.txt(f"{t['name']:<15} {m.coverage[i]:5.0f}%  /  {m.returned[i]:.0f} MB received",-.74,.005-i*.047,.78)
        self.txt(wrap(r['outcome'],54),.03,.25,.92)
        self.txt(f"Data returned: {m.fraction*100:.1f}%\nRemaining propellant: {m.fuel:.1f} kg\nBudget used: {r['cost']} / 260 M credits\nHealth: {m.health:.0f}%",.03,.10,.85,CYAN)
        self.txt(wrap('Score: 50 points for regional coverage, 30 for data returned, 10 for capture, and up to 10 for budget efficiency.',55),.03,-.06,.77,MUTED)
        lesson=('Larger arrays support more active time. Radio scheduling frees storage; finer cameras only help if their data reaches Earth.' if r['success'] else 'Inspect the readiness warnings. Fuel enables capture, solar power sustains operations, and the radio turns stored images into returned science.')
        self.txt(wrap(lesson,55),.03,-.18,.8)
        self.btn('MAIN MENU',-.65,-.42,lambda:self.show('menu'),.28)
        self.btn('COMPARE RUNS',0,-.42,lambda:self.show('compare'),.32)
        self.btn('REDESIGN & RETRY',.60,-.42,lambda:self.show('designer'),.38,True)
    def screen_compare(self):
        self.header('Mission archive','Compare your flights','Latest ten completed runs. The manifest is retained in your local save.')
        panel(self.ui,0,-.02,1.6,.64)
        self.txt('RUN       STATUS                  SCORE             COST',-.71,.24,.9,CYAN)
        for i,r in enumerate(self.history[-8:]):self.txt(f"{i+1:02d}         {'SUCCESS' if r['success'] else 'INCOMPLETE':<15}   {r['score']:3d} / 100         {r['cost']:.0f} M",-.71,.18-i*.057,.86)
        self.btn('BACK',-.65,-.42,lambda:self.show('results'),.25)
    def open_settings(self,return_screen):self.return_screen=return_screen;self.show('settings')
    def setting(self,key):
        if key in ('master','music','sfx'):self.settings[key]=round((self.settings[key]+.25)%1.25,2)
        else:self.settings[key]=not self.settings[key]
        self.audio.apply();self.world.stars.enabled=not self.settings['low_graphics'];self.persist();self.show('settings')
    def screen_settings(self):
        self.header('Preferences','Make yourself comfortable')
        panel(self.ui,0,-.01,1.35,.62)
        for i,(key,title) in enumerate([('master','Master volume'),('music','Ambient music'),('sfx','Sound effects'),('mute','Mute all audio'),('reduced_motion','Reduced motion'),('low_graphics','Low graphics / hide stars')]):
            self.txt(title,-.56,.22-i*.075,.96)
            v=self.settings[key];s=('ON' if v else 'OFF') if type(v) is bool else f'{v*100:.0f}%  /  CLICK TO CYCLE'
            self.btn(s,.35,.21-i*.075,lambda k=key:self.setting(k),.45)
        self.btn('BACK',-.55,-.42,lambda:self.show(self.return_screen),.25)
        self.btn('TOGGLE FULLSCREEN [F11]',.40,-.42,self.fullscreen,.52)
    def fullscreen(self):window.fullscreen=not window.fullscreen
    def screen_guide(self):
        self.header('Field manual','Your first flight','Use the balanced default design for a guided first attempt.')
        panel(self.ui,0,-.015,1.6,.65)
        self.txt('FLIGHT CHECKLIST',-.74,.25,.9,CYAN)
        steps=['1. Inspect hardware; the defaults can complete the mission.','2. Keep Aster 2, Hohmann window and Low mapping orbit.','3. Review the checks and begin the cinematic launch.','4. After capture, select Jezero and click CAMERA.','5. Enable DOWNLINK early. It waits for Earth visibility.','6. At 80% coverage, choose another region and rearm.','7. Switch away from dusty regions until hour 5.','8. Return 80% of all data before operations hour 24.']
        self.txt('\n\n'.join(steps),-.74,.19,.82)
        self.txt('CONTROLS',.25,.25,.9,CYAN)
        self.txt('Right-drag  Rotate view\nWheel          Zoom\nR                 Reset view\n1 / 2 / 3       Camera modes\nSpace           Pause mission\nI                   Camera on/off\nT                  Radio on/off\nEscape         Pause / resume\nF11               Fullscreen',.25,.19,.85)
        self.txt('1x time: 1 real second =\n1 simulated minute in orbit.\n\n4x and 12x speed up operations.\nPause before making decisions.',.25,-.12,.8,MUTED)
        self.btn('BACK',-.65,-.42,lambda:self.show('menu'),.26)
    def screen_credits(self):
        self.header('Sources & credits','Built for curiosity','Independent student project. Not an official NASA product or endorsement.')
        panel(self.ui,0,-.02,1.6,.64)
        self.txt('SCIENCE & IMAGERY',-.74,.25,.9,CYAN)
        self.txt('Mars texture: NASA / JPL-Caltech; Viking images\nprocessed by USGS, NASA 3D Resources.\n\nMars constants: NASA NSSDC Mars Fact Sheet.\nTargets: NASA Mars landing-site studies and\nPDS Geosciences Orbital Data Explorer.\n\nEngineering inspiration: NASA CubeSat 101\nand supplied mission-design reference papers.',-.74,.19,.85)
        self.txt('CRAFT & MODEL',.10,.25,.9,CYAN)
        self.txt('Python 3.12 / Ursina 8.3 / Panda3D\nOriginal procedural orbiter and Earth artwork.\nOriginal synthesized ambient music and effects.\n\nHardware, budgets and events: game assumptions.\nReal formulas: rocket equation, vis-viva,\nKepler period and inverse-square solar power.\n\nGeometry, timing and coverage are simplified.\nFull attribution and limits: docs/SCIENCE.md',.10,.19,.85)
        self.btn('BACK',-.65,-.42,lambda:self.show('menu'),.26)
    def quit(self):self.persist();application.quit()
    def update(self):
        dt=min(time.dt,.1);self.clock+=dt
        if abs(camera.aspect_ratio-self.last_aspect)>.001:self.fit_ui()
        self.world.drag()
        self.world.tick(0 if self.mission and self.screen=='simulation' and self.mission.paused else dt,self.mission if self.screen=='simulation' else None,self.settings['reduced_motion'])
        if self.screen=='simulation':
            m=self.mission;old=m.phase;m.advance(dt)
            if m.phase=='Results':self.record_result();return
            if old!=m.phase:self.audio.play('milestone')
            if m.message!=self.last_message:
                if m.message.startswith('Image stored'):self.audio.play('image')
                elif any(x in m.message for x in ('POWER','STORAGE','Dust')):self.audio.play('warning')
                self.last_message=m.message
            self.ui_tick+=dt
            if self.ui_tick>.15:self.ui_tick=0;self.refresh_telemetry()
            self.auto_save+=dt
            if self.auto_save>15:self.auto_save=0;self.persist()
    def input(self,key):
        self.world.input(key)
        if key=='f11':self.fullscreen()
        if self.screen=='simulation':
            if key in ('space','escape'):self.pause()
            if key=='i':self.toggle_image()
            if key=='t':self.toggle_radio()
        elif key=='escape':
            if self.screen=='confirm_end':self.keep_flying()
            elif self.screen in ('results','compare'):self.show('menu')
            elif self.screen!='menu':self.show('menu')
