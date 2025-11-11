# grundlage.py
from framework.framework import Framework
from .code import Code
from .held import Held
from .knappe import Knappe

# Platzhalter für globale Variablen, die beim Level-Laden gefüllt werden


class LevelManager:
    """Verwaltet den Ladevorgang der Level und stellt den Helden bereit."""
    def __init__(self):
        self.framework = None
        self.held = None

    def lade(self, nummer: int, weiblich = False,splash = False):
        global held,framework
        """Lädt das angegebene Level und initialisiert das Framework."""
        import sys

        self.framework = Framework(levelnummer=nummer, auto_erzeuge_objekte=True,w = weiblich,splash=splash)
        self.held = self.framework.spielfeld.held
        held = self.held
        framework = self.framework

        # Hinweis und Status zurücksetzen
        self.framework._hinweis = None
        self.framework._aktion_blockiert = False
        # Expose entity constructors in this module so student code that does
        # `from framework.grundlage import *` after calling level.lade(...) will
        # have convenient access to the classes referenced by the level.
        try:
            sp = getattr(self.framework, 'spielfeld', None)
        except Exception:
            sp = None

        # Export a full set of canonical entity/class names so students can
        # construct any framework object from `framework.grundlage` regardless
        # of whether the level actually spawns one. When student_mode is
        # enabled, only student-provided classes will be exported (so exercises
        # that require students to implement classes remain enforced).
        canonical_names = [
            'Held', 'Herz', 'Monster', 'Bogenschuetze', 'Code', 'Tuer',
            'Schluessel', 'Villager', 'Questgeber', 'Knappe', 'Tor', 'Hindernis', 'Gegenstand'
        ]

        # helper: import framework classes for fallbacks
        try:
            from .hindernis import Hindernis as _Hindernis
        except Exception:
            _Hindernis = None
        try:
            from .tuer import Tuer as _Tuer
        except Exception:
            _Tuer = None
        try:
            from .tor import Tor as _Tor
        except Exception:
            _Tor = None
        try:
            from .schluessel import Schluessel as _Schluessel
        except Exception:
            _Schluessel = None
        try:
            from .knappe import Knappe as _Knappe
        except Exception:
            _Knappe = None
        try:
            from .monster import Monster as _Monster, Bogenschuetze as _Bogenschuetze
        except Exception:
            _Monster = None; _Bogenschuetze = None
        try:
            from .herz import Herz as _Herz
        except Exception:
            _Herz = None
        try:
            from .code import Code as _Code
        except Exception:
            _Code = None
        try:
            from .villager import Villager as _Villager, Questgeber as _Questgeber
        except Exception:
            _Villager = None; _Questgeber = None

        # Decide whether student classes are enabled in this level
        try:
            settings = getattr(sp, 'settings', {}) or {}
            student_mode = bool(settings.get('import_pfad') or settings.get('use_student_module') or settings.get('student_classes_in_subfolder'))
        except Exception:
            student_mode = False

        # Flexible wrapper factory to accept both (name,x,y) and (x,y,name)
        def _flexible_ctor(fwcls):
            def _ctor(*args, **kwargs):
                try:
                    # pattern: (name, x, y)
                    if len(args) >= 3 and isinstance(args[0], str) and isinstance(args[1], int) and isinstance(args[2], int):
                        name, x, y = args[0], args[1], args[2]
                        return fwcls(x, y, name, **kwargs)
                    # pattern: (x, y, name)
                    if len(args) >= 2 and isinstance(args[0], int) and isinstance(args[1], int):
                        x, y = args[0], args[1]
                        name = args[2] if len(args) > 2 else kwargs.get('name', None)
                        if name is None:
                            return fwcls(x, y, **kwargs)
                        return fwcls(x, y, name, **kwargs)
                    # fallback: try direct construction
                    return fwcls(*args, **kwargs)
                except Exception:
                    return fwcls(*args, **kwargs)
            return _ctor

        import sys as _sys
        _mod = _sys.modules.get(__name__)
        for cname in canonical_names:
            try:
                # map canonical to framework class for fallback
                fwcls = None
                if cname == 'Hindernis': fwcls = _Hindernis
                elif cname == 'Tuer': fwcls = _Tuer
                elif cname == 'Tor': fwcls = _Tor
                elif cname == 'Schluessel': fwcls = _Schluessel
                elif cname == 'Knappe': fwcls = _Knappe
                elif cname == 'Monster': fwcls = _Monster
                elif cname == 'Bogenschuetze': fwcls = _Bogenschuetze
                elif cname == 'Herz': fwcls = _Herz
                elif cname == 'Code': fwcls = _Code
                elif cname == 'Villager': fwcls = _Villager
                elif cname == 'Questgeber': fwcls = _Questgeber
                elif cname == 'Held':
                    # expose Held class wrapper that constructs the framework Held
                    try:
                        from .held import Held as _Held
                        fwcls = _Held
                    except Exception:
                        fwcls = None
                else:
                    fwcls = None

                cls = None
                try:
                    if sp is not None and fwcls is not None:
                        cls = sp._get_entity_class(cname, fwcls)
                    elif sp is not None:
                        cls = sp._get_entity_class(cname, None)
                    else:
                        cls = None
                except Exception:
                    cls = None

                # Decide export: if student_mode requested, only export student classes
                if student_mode:
                    # if a student class was found, export it; otherwise skip export
                    if cls is None:
                        # ensure name not present
                        if hasattr(_mod, cname):
                            try:
                                delattr(_mod, cname)
                            except Exception:
                                pass
                        continue
                    else:
                        # export student class (as-is)
                        try:
                            setattr(_mod, cname, cls)
                        except Exception:
                            pass
                else:
                    # student mode not requested: export framework class (wrap if necessary)
                    if cls is None:
                        cls = fwcls
                    if cls is None:
                        continue
                    # if exporting an internal framework class that expects (x,y,...) but students
                    # may call (name,x,y), provide a flexible wrapper
                    try:
                        if cls is fwcls and fwcls is not None:
                            setattr(_mod, cname, _flexible_ctor(fwcls))
                        else:
                            setattr(_mod, cname, cls)
                    except Exception:
                        try:
                            setattr(_mod, cname, cls)
                        except Exception:
                            pass
            except Exception:
                continue
        
    def gib_objekt_bei(self,x,y):
        return framework.gib_objekt_an(x,y)

    def objekt_hinzufuegen(self, obj):
        """Convenience: forward to the active framework instance so students
        can call `level.objekt_hinzufuegen(obj)` directly from their code.
        """
        try:
            fw = getattr(self, 'framework', None)
            if fw is None:
                # fallback to module-level framework if available
                try:
                    from framework import grundlage as _g
                    fw = getattr(_g, 'framework', None)
                except Exception:
                    fw = None
            if fw is None:
                raise AttributeError('Kein Framework vorhanden')
            return fw.objekt_hinzufuegen(obj)
        except Exception:
            # Bubble up the AttributeError to make student errors visible
            raise
        
 
"""
def __getattr__(name):
    if name == "held":
        return level.framework.spielfeld.held
    if name == "framework":
        return level.framework
    raise AttributeError(name)
"""




# Globale Instanz
global held, framework
level = LevelManager()
held = None
framework = None
tuer = None
code = None
monster = None


# Optional: Direkter Start bei eigenständigem Aufruf (z. B. Test)
"""
if __name__ == "__main__":
    level.lade(1)
    framework.starten()
"""
