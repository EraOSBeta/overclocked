# Released under AGPL-3.0-or-later. See LICENSE for details.
#
# This file incorporates work covered by the following permission notice:
#   Released under the MIT License. See LICENSE for details.
#
"""Ballistica scene api version 1. Basically all gameplay related code."""

# ba_meta require api 8

# The stuff we expose here at the top level is our 'public' api for use
# from other modules/packages. Code *within* this package should import
# things from this package's submodules directly to reduce the chance of
# dependency loops. The exception is TYPE_CHECKING blocks and
# annotations since those aren't evaluated at runtime.

import logging

# Aside from our own stuff, we also bundle a number of things from ba or
# other modules; the goal is to let most simple mods rely solely on this
# module to keep things simple.

from efro.util import set_canonical_module_names
from babase import (
    app,
    AppIntent,
    AppIntentDefault,
    AppIntentExec,
    AppMode,
    apptime,
    AppTime,
    apptimer,
    AppTimer,
    Call,
    ContextError,
    ContextRef,
    displaytime,
    DisplayTime,
    displaytimer,
    DisplayTimer,
    existing,
    fade_screen,
    get_remote_app_name,
    increment_analytics_count,
    InputType,
    is_point_in_box,
    lock_all_input,
    Lstr,
    NodeNotFoundError,
    normalized_color,
    NotFoundError,
    PlayerNotFoundError,
    Plugin,
    pushcall,
    safecolor,
    screenmessage,
    set_analytics_screen,
    storagename,
    timestring,
    UIScale,
    unlock_all_input,
    Vec3,
    WeakCall,
)

from _bascenev1 import (
    ActivityData,
    basetime,
    basetimer,
    BaseTimer,
    camerashake,
    capture_gamepad_input,
    capture_keyboard_input,
    chatmessage,
    client_info_query_response,
    CollisionMesh,
    connect_to_party,
    Data,
    disconnect_client,
    disconnect_from_host,
    emitfx,
    end_host_scanning,
    get_chat_messages,
    get_connection_to_host_info,
    get_connection_to_host_info_2,
    get_foreground_host_activity,
    get_foreground_host_session,
    get_game_port,
    get_game_roster,
    get_local_active_input_devices_count,
    get_public_party_enabled,
    get_public_party_max_size,
    get_random_names,
    get_replay_speed_exponent,
    get_ui_input_device,
    getactivity,
    getcollisionmesh,
    getdata,
    getinputdevice,
    getmesh,
    getnodes,
    getsession,
    getsound,
    gettexture as vc_unsafe_gettexture,
    have_connected_clients,
    have_touchscreen_input,
    host_scan_cycle,
    InputDevice,
    is_in_replay,
    ls_input_devices,
    ls_objects,
    Material,
    Mesh,
    new_host_session,
    new_replay_session,
    newactivity,
    newnode,
    Node,
    printnodes,
    protocol_version,
    release_gamepad_input,
    release_keyboard_input,
    reset_random_player_names,
    broadcastmessage,
    SessionData,
    SessionPlayer,
    set_admins,
    set_authenticate_clients,
    set_debug_speed_exponent,
    set_enable_default_kick_voting,
    set_internal_music,
    set_map_bounds,
    set_master_server_source,
    set_public_party_enabled,
    set_public_party_max_size,
    set_public_party_name,
    set_public_party_queue_enabled,
    set_public_party_stats_url,
    set_replay_speed_exponent,
    set_touchscreen_editing,
    Sound,
    Texture,
    time,
    timer,
    Timer,
)
from bascenev1._activity import Activity
from bascenev1._activitytypes import JoinActivity, ScoreScreenActivity
from bascenev1._actor import (
    Actor,
    ActorMode,
    ProjectileActorMode,
    SmashActorMode,
)
from bascenev1._appmode import SceneV1AppMode
from bascenev1._campaign import init_campaigns, Campaign
from bascenev1._collision import Collision, getcollision
from bascenev1._coopgame import CoopGameActivity
from bascenev1._coopsession import CoopSession
from bascenev1._debug import print_live_object_warnings
from bascenev1._dependency import (
    Dependency,
    DependencyComponent,
    DependencySet,
    AssetPackage,
)
from bascenev1._dualteamsession import DualTeamSession
from bascenev1._freeforallsession import FreeForAllSession
from bascenev1._gameactivity import GameActivity
from bascenev1._gameresults import GameResults
from bascenev1._gameutils import (
    animate,
    animate_array,
    BaseTime,
    cameraflash,
    GameTip,
    get_trophy_string,
    show_damage_count,
    Time,
)
from bascenev1._level import Level
from bascenev1._lobby import Lobby, Chooser
from bascenev1._map import (
    get_filtered_map_name,
    get_map_class,
    get_map_display_string,
    Map,
    register_map,
)
from bascenev1._messages import (
    CelebrateMessage,
    DeathType,
    DieMessage,
    DropMessage,
    DroppedMessage,
    FreezeMessage,
    HitMessage,
    ImpactDamageMessage,
    OutOfBoundsMessage,
    PickedUpMessage,
    PickUpMessage,
    PlayerDiedMessage,
    PlayerProfilesChangedMessage,
    ShouldShatterMessage,
    StandMessage,
    ThawMessage,
    UNHANDLED,
)
from bascenev1._multiteamsession import (
    MultiTeamSession,
    DEFAULT_TEAM_COLORS,
    DEFAULT_TEAM_NAMES,
)
from bascenev1._music import MusicType, setmusic
from bascenev1._net import HostInfo
from bascenev1._nodeactor import NodeActor
from bascenev1._powerup import get_default_powerup_distribution
from bascenev1._profile import (
    get_player_colors,
    get_player_profile_icon,
    get_player_profile_colors,
)
from bascenev1._player import PlayerInfo, Player, EmptyPlayer, StandLocation
from bascenev1._playlist import (
    get_default_free_for_all_playlist,
    get_default_teams_playlist,
    filter_playlist,
)
from bascenev1._powerup import PowerupMessage, PowerupAcceptMessage
from bascenev1._score import ScoreType, ScoreConfig
from bascenev1._settings import (
    BoolSetting,
    ChoiceSetting,
    FloatChoiceSetting,
    FloatSetting,
    IntChoiceSetting,
    IntSetting,
    Setting,
)
from bascenev1._session import Session, set_player_rejoin_cooldown
from bascenev1._stats import PlayerScoredMessage, PlayerRecord, Stats
from bascenev1._team import SessionTeam, Team, EmptyTeam
from bascenev1._teamgame import TeamGameActivity


def gettexture(name: str) -> Texture:
    """Return a texture, loading it if necessary.

    Category: **Asset Functions**

    Note that this function returns immediately even if the asset has yet
    to be loaded. To avoid hitches, instantiate your asset objects in
    advance of when you will be using them, allowing time for them to
    load in the background if necessary.

    This is a replacement of the actual bascenev1.gettexture, meant to be safe
    to use in Vanillaclocked.
    """
    if app.config.get('Vanillaclocked', False):
        if name == 'overclockedLogo':
            return vc_unsafe_gettexture('logo')
        if name == 'powerupPap':
            return vc_unsafe_gettexture('achievementSuperPunch')
        if name == 'powerupUno':
            return vc_unsafe_gettexture('replayIcon')
        if name == 'powerupInv':
            return vc_unsafe_gettexture('levelIcon')
        if name == 'powerupBigBombs':
            return vc_unsafe_gettexture('buttonBomb')
        if name == 'powerupLightBombs':
            return vc_unsafe_gettexture('nextLevelIcon')
        if name == 'powerupPowerups':
            return vc_unsafe_gettexture('chestIcon')
        if name == 'powerupBot':
            return vc_unsafe_gettexture('cyborgIcon')
        if name == 'powerupImpulseBombs':
            return vc_unsafe_gettexture('achievementCrossHair')
        if name == 'powerupIcepactBombs':
            return vc_unsafe_gettexture('bombColorIce')
        if name == 'powerupWonderBombs':
            return vc_unsafe_gettexture('egg4')
        if name == 'powerupPortal':
            return vc_unsafe_gettexture('landMineLit')
        if name == 'powerup0g':
            return vc_unsafe_gettexture('upButton')
        if name == 'powerupCoins':
            return vc_unsafe_gettexture('coin')
        if name == 'powerupDev':
            return vc_unsafe_gettexture('shield')
        if name == 'wonderBombColor':
            return vc_unsafe_gettexture('white')
    return vc_unsafe_gettexture(name)


__all__ = [
    'Activity',
    'ActivityData',
    'Actor',
    'ActorMode',
    'ProjectileActorMode',
    'SmashActorMode',
    'animate',
    'animate_array',
    'app',
    'AppIntent',
    'AppIntentDefault',
    'AppIntentExec',
    'AppMode',
    'AppTime',
    'apptime',
    'apptimer',
    'AppTimer',
    'AssetPackage',
    'basetime',
    'BaseTime',
    'basetimer',
    'BaseTimer',
    'BoolSetting',
    'Call',
    'cameraflash',
    'camerashake',
    'Campaign',
    'capture_gamepad_input',
    'capture_keyboard_input',
    'CelebrateMessage',
    'chatmessage',
    'ChoiceSetting',
    'Chooser',
    'client_info_query_response',
    'Collision',
    'CollisionMesh',
    'connect_to_party',
    'ContextError',
    'ContextRef',
    'CoopGameActivity',
    'CoopSession',
    'Data',
    'DeathType',
    'DEFAULT_TEAM_COLORS',
    'DEFAULT_TEAM_NAMES',
    'Dependency',
    'DependencyComponent',
    'DependencySet',
    'DieMessage',
    'disconnect_client',
    'disconnect_from_host',
    'displaytime',
    'DisplayTime',
    'displaytimer',
    'DisplayTimer',
    'DropMessage',
    'DroppedMessage',
    'DualTeamSession',
    'emitfx',
    'EmptyPlayer',
    'EmptyTeam',
    'end_host_scanning',
    'existing',
    'fade_screen',
    'filter_playlist',
    'FloatChoiceSetting',
    'FloatSetting',
    'FreeForAllSession',
    'FreezeMessage',
    'GameActivity',
    'GameResults',
    'GameTip',
    'get_chat_messages',
    'get_connection_to_host_info',
    'get_connection_to_host_info_2',
    'get_default_free_for_all_playlist',
    'get_default_teams_playlist',
    'get_default_powerup_distribution',
    'get_filtered_map_name',
    'get_foreground_host_activity',
    'get_foreground_host_session',
    'get_game_port',
    'get_game_roster',
    'get_game_roster',
    'get_local_active_input_devices_count',
    'get_map_class',
    'get_map_display_string',
    'get_player_colors',
    'get_player_profile_colors',
    'get_player_profile_icon',
    'get_public_party_enabled',
    'get_public_party_max_size',
    'get_random_names',
    'get_remote_app_name',
    'get_replay_speed_exponent',
    'get_trophy_string',
    'get_ui_input_device',
    'getactivity',
    'getcollision',
    'getcollisionmesh',
    'getdata',
    'getinputdevice',
    'getmesh',
    'getnodes',
    'getsession',
    'getsound',
    'gettexture',
    'have_connected_clients',
    'have_touchscreen_input',
    'HitMessage',
    'HostInfo',
    'host_scan_cycle',
    'ImpactDamageMessage',
    'increment_analytics_count',
    'init_campaigns',
    'InputDevice',
    'InputType',
    'IntChoiceSetting',
    'IntSetting',
    'is_in_replay',
    'is_point_in_box',
    'JoinActivity',
    'Level',
    'Lobby',
    'lock_all_input',
    'ls_input_devices',
    'ls_objects',
    'Lstr',
    'Map',
    'Material',
    'Mesh',
    'MultiTeamSession',
    'MusicType',
    'new_host_session',
    'new_replay_session',
    'newactivity',
    'newnode',
    'Node',
    'NodeActor',
    'NodeNotFoundError',
    'normalized_color',
    'NotFoundError',
    'OutOfBoundsMessage',
    'PickedUpMessage',
    'PickUpMessage',
    'Player',
    'PlayerDiedMessage',
    'PlayerProfilesChangedMessage',
    'PlayerInfo',
    'PlayerNotFoundError',
    'PlayerRecord',
    'PlayerScoredMessage',
    'Plugin',
    'PowerupAcceptMessage',
    'PowerupMessage',
    'print_live_object_warnings',
    'printnodes',
    'protocol_version',
    'pushcall',
    'register_map',
    'release_gamepad_input',
    'release_keyboard_input',
    'reset_random_player_names',
    'safecolor',
    'screenmessage',
    'SceneV1AppMode',
    'ScoreConfig',
    'ScoreScreenActivity',
    'ScoreType',
    'broadcastmessage',
    'Session',
    'SessionData',
    'SessionPlayer',
    'SessionTeam',
    'set_admins',
    'set_analytics_screen',
    'set_authenticate_clients',
    'set_debug_speed_exponent',
    'set_debug_speed_exponent',
    'set_enable_default_kick_voting',
    'set_internal_music',
    'set_map_bounds',
    'set_master_server_source',
    'set_public_party_enabled',
    'set_public_party_max_size',
    'set_public_party_name',
    'set_public_party_queue_enabled',
    'set_public_party_stats_url',
    'set_player_rejoin_cooldown',
    'set_replay_speed_exponent',
    'set_touchscreen_editing',
    'setmusic',
    'Setting',
    'ShouldShatterMessage',
    'show_damage_count',
    'Sound',
    'StandLocation',
    'StandMessage',
    'Stats',
    'storagename',
    'Team',
    'TeamGameActivity',
    'Texture',
    'ThawMessage',
    'time',
    'Time',
    'timer',
    'Timer',
    'timestring',
    'UIScale',
    'UNHANDLED',
    'unlock_all_input',
    'Vec3',
    'WeakCall',
]

# We want stuff here to show up as bascenev1.Foo instead of
# bascenev1._submodule.Foo.
set_canonical_module_names(globals())

# Sanity check: we want to keep ballistica's dependencies and
# bootstrapping order clearly defined; let's check a few particular
# modules to make sure they never directly or indirectly import us
# before their own execs complete.
if __debug__:
    for _mdl in 'babase', '_babase':
        if not hasattr(__import__(_mdl), '_REACHED_END_OF_MODULE'):
            logging.warning(
                '%s was imported before %s finished importing;'
                ' should not happen.',
                __name__,
                _mdl,
            )
