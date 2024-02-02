from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class CanvasRect:
    class Meta:
        name = "canvasRect"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    width: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    height: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class CanvasScrollPosition:
    class Meta:
        name = "canvasScrollPosition"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class Color:
    class Meta:
        name = "color"

    r: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    g: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    b: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    a: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class Fields:
    class Meta:
        name = "fields"

    title: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    value: Optional[Union[str, int]] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    type: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    type_string: Optional[str] = field(
        default=None,
        metadata={
            "name": "typeString",
            "type": "Element",
        }
    )


@dataclass
class MGameObject:
    class Meta:
        name = "m_GameObject"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class MPersistentCalls:
    class Meta:
        name = "m_PersistentCalls"

    m_calls: List[object] = field(
        default_factory=list,
        metadata={
            "name": "m_Calls",
            "type": "Element",
        }
    )


@dataclass
class MScript:
    class Meta:
        name = "m_Script"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class OutgoingLinks:
    class Meta:
        name = "outgoingLinks"

    origin_conversation_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "originConversationID",
            "type": "Element",
        }
    )
    origin_dialogue_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "originDialogueID",
            "type": "Element",
        }
    )
    destination_conversation_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "destinationConversationID",
            "type": "Element",
        }
    )
    destination_dialogue_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "destinationDialogueID",
            "type": "Element",
        }
    )
    is_connector: Optional[int] = field(
        default=None,
        metadata={
            "name": "isConnector",
            "type": "Element",
        }
    )
    priority: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class OverrideSettings:
    class Meta:
        name = "overrideSettings"

    use_overrides: Optional[int] = field(
        default=None,
        metadata={
            "name": "useOverrides",
            "type": "Element",
        }
    )
    override_subtitle_settings: Optional[int] = field(
        default=None,
        metadata={
            "name": "overrideSubtitleSettings",
            "type": "Element",
        }
    )
    show_npcsubtitles_during_line: Optional[int] = field(
        default=None,
        metadata={
            "name": "showNPCSubtitlesDuringLine",
            "type": "Element",
        }
    )
    show_npcsubtitles_with_responses: Optional[int] = field(
        default=None,
        metadata={
            "name": "showNPCSubtitlesWithResponses",
            "type": "Element",
        }
    )
    show_pcsubtitles_during_line: Optional[int] = field(
        default=None,
        metadata={
            "name": "showPCSubtitlesDuringLine",
            "type": "Element",
        }
    )
    skip_pcsubtitle_after_response_menu: Optional[int] = field(
        default=None,
        metadata={
            "name": "skipPCSubtitleAfterResponseMenu",
            "type": "Element",
        }
    )
    subtitle_chars_per_second: Optional[float] = field(
        default=None,
        metadata={
            "name": "subtitleCharsPerSecond",
            "type": "Element",
        }
    )
    min_subtitle_seconds: Optional[float] = field(
        default=None,
        metadata={
            "name": "minSubtitleSeconds",
            "type": "Element",
        }
    )
    continue_button: Optional[int] = field(
        default=None,
        metadata={
            "name": "continueButton",
            "type": "Element",
        }
    )
    override_sequence_settings: Optional[int] = field(
        default=None,
        metadata={
            "name": "overrideSequenceSettings",
            "type": "Element",
        }
    )
    default_sequence: Optional[object] = field(
        default=None,
        metadata={
            "name": "defaultSequence",
            "type": "Element",
        }
    )
    default_player_sequence: Optional[object] = field(
        default=None,
        metadata={
            "name": "defaultPlayerSequence",
            "type": "Element",
        }
    )
    default_response_menu_sequence: Optional[object] = field(
        default=None,
        metadata={
            "name": "defaultResponseMenuSequence",
            "type": "Element",
        }
    )
    override_input_settings: Optional[int] = field(
        default=None,
        metadata={
            "name": "overrideInputSettings",
            "type": "Element",
        }
    )
    always_force_response_menu: Optional[int] = field(
        default=None,
        metadata={
            "name": "alwaysForceResponseMenu",
            "type": "Element",
        }
    )
    include_invalid_entries: Optional[int] = field(
        default=None,
        metadata={
            "name": "includeInvalidEntries",
            "type": "Element",
        }
    )
    response_timeout: Optional[float] = field(
        default=None,
        metadata={
            "name": "responseTimeout",
            "type": "Element",
        }
    )


@dataclass
class Portrait:
    class Meta:
        name = "portrait"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class SpritePortrait:
    class Meta:
        name = "spritePortrait"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class SyncActorsDatabase:
    class Meta:
        name = "syncActorsDatabase"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class SyncItemsDatabase:
    class Meta:
        name = "syncItemsDatabase"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class SyncLocationsDatabase:
    class Meta:
        name = "syncLocationsDatabase"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class SyncVariablesDatabase:
    class Meta:
        name = "syncVariablesDatabase"

    m_file_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_FileID",
            "type": "Element",
        }
    )
    m_path_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_PathID",
            "type": "Element",
        }
    )


@dataclass
class Actors:
    class Meta:
        name = "actors"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    fields: List[Fields] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    portrait: Optional[Portrait] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    sprite_portrait: Optional[SpritePortrait] = field(
        default=None,
        metadata={
            "name": "spritePortrait",
            "type": "Element",
        }
    )
    alternate_portraits: List[object] = field(
        default_factory=list,
        metadata={
            "name": "alternatePortraits",
            "type": "Element",
        }
    )
    sprite_portraits: List[object] = field(
        default_factory=list,
        metadata={
            "name": "spritePortraits",
            "type": "Element",
        }
    )


@dataclass
class EmphasisSettings:
    class Meta:
        name = "emphasisSettings"

    color: Optional[Color] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    bold: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    italic: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    underline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class Items:
    class Meta:
        name = "items"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    fields: List[Fields] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class Locations:
    class Meta:
        name = "locations"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    fields: List[Fields] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class OnExecute:
    class Meta:
        name = "onExecute"

    m_persistent_calls: Optional[MPersistentCalls] = field(
        default=None,
        metadata={
            "name": "m_PersistentCalls",
            "type": "Element",
        }
    )


@dataclass
class SyncInfo:
    class Meta:
        name = "syncInfo"

    sync_actors: Optional[int] = field(
        default=None,
        metadata={
            "name": "syncActors",
            "type": "Element",
        }
    )
    sync_items: Optional[int] = field(
        default=None,
        metadata={
            "name": "syncItems",
            "type": "Element",
        }
    )
    sync_locations: Optional[int] = field(
        default=None,
        metadata={
            "name": "syncLocations",
            "type": "Element",
        }
    )
    sync_variables: Optional[int] = field(
        default=None,
        metadata={
            "name": "syncVariables",
            "type": "Element",
        }
    )
    sync_actors_database: Optional[SyncActorsDatabase] = field(
        default=None,
        metadata={
            "name": "syncActorsDatabase",
            "type": "Element",
        }
    )
    sync_items_database: Optional[SyncItemsDatabase] = field(
        default=None,
        metadata={
            "name": "syncItemsDatabase",
            "type": "Element",
        }
    )
    sync_locations_database: Optional[SyncLocationsDatabase] = field(
        default=None,
        metadata={
            "name": "syncLocationsDatabase",
            "type": "Element",
        }
    )
    sync_variables_database: Optional[SyncVariablesDatabase] = field(
        default=None,
        metadata={
            "name": "syncVariablesDatabase",
            "type": "Element",
        }
    )


@dataclass
class Variables:
    class Meta:
        name = "variables"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    fields: List[Fields] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )


@dataclass
class DialogueEntries:
    class Meta:
        name = "dialogueEntries"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    fields: List[Fields] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    conversation_id: Optional[int] = field(
        default=None,
        metadata={
            "name": "conversationID",
            "type": "Element",
        }
    )
    is_root: Optional[int] = field(
        default=None,
        metadata={
            "name": "isRoot",
            "type": "Element",
        }
    )
    is_group: Optional[int] = field(
        default=None,
        metadata={
            "name": "isGroup",
            "type": "Element",
        }
    )
    node_color: Optional[object] = field(
        default=None,
        metadata={
            "name": "nodeColor",
            "type": "Element",
        }
    )
    delay_sim_status: Optional[int] = field(
        default=None,
        metadata={
            "name": "delaySimStatus",
            "type": "Element",
        }
    )
    false_condition_action: Optional[object] = field(
        default=None,
        metadata={
            "name": "falseConditionAction",
            "type": "Element",
        }
    )
    condition_priority: Optional[int] = field(
        default=None,
        metadata={
            "name": "conditionPriority",
            "type": "Element",
        }
    )
    outgoing_links: List[OutgoingLinks] = field(
        default_factory=list,
        metadata={
            "name": "outgoingLinks",
            "type": "Element",
        }
    )
    conditions_string: Optional[Union[str, bool]] = field(
        default=None,
        metadata={
            "name": "conditionsString",
            "type": "Element",
        }
    )
    user_script: Optional[str] = field(
        default=None,
        metadata={
            "name": "userScript",
            "type": "Element",
        }
    )
    on_execute: Optional[OnExecute] = field(
        default=None,
        metadata={
            "name": "onExecute",
            "type": "Element",
        }
    )
    canvas_rect: Optional[CanvasRect] = field(
        default=None,
        metadata={
            "name": "canvasRect",
            "type": "Element",
        }
    )


@dataclass
class Conversations:
    class Meta:
        name = "conversations"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    fields: List[Fields] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    override_settings: Optional[OverrideSettings] = field(
        default=None,
        metadata={
            "name": "overrideSettings",
            "type": "Element",
        }
    )
    node_color: Optional[object] = field(
        default=None,
        metadata={
            "name": "nodeColor",
            "type": "Element",
        }
    )
    dialogue_entries: List[DialogueEntries] = field(
        default_factory=list,
        metadata={
            "name": "dialogueEntries",
            "type": "Element",
        }
    )
    canvas_scroll_position: Optional[CanvasScrollPosition] = field(
        default=None,
        metadata={
            "name": "canvasScrollPosition",
            "type": "Element",
        }
    )
    canvas_zoom: Optional[float] = field(
        default=None,
        metadata={
            "name": "canvasZoom",
            "type": "Element",
        }
    )


@dataclass
class Discopy:
    class Meta:
        name = "discopy"

    m_game_object: Optional[MGameObject] = field(
        default=None,
        metadata={
            "name": "m_GameObject",
            "type": "Element",
        }
    )
    m_enabled: Optional[int] = field(
        default=None,
        metadata={
            "name": "m_Enabled",
            "type": "Element",
        }
    )
    m_script: Optional[MScript] = field(
        default=None,
        metadata={
            "name": "m_Script",
            "type": "Element",
        }
    )
    m_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "m_Name",
            "type": "Element",
        }
    )
    version: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    author: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    description: Optional[object] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    global_user_script: Optional[object] = field(
        default=None,
        metadata={
            "name": "globalUserScript",
            "type": "Element",
        }
    )
    emphasis_settings: List[EmphasisSettings] = field(
        default_factory=list,
        metadata={
            "name": "emphasisSettings",
            "type": "Element",
        }
    )
    actors: List[Actors] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    items: List[Items] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    locations: List[Locations] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    variables: List[Variables] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    conversations: List[Conversations] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    sync_info: Optional[SyncInfo] = field(
        default=None,
        metadata={
            "name": "syncInfo",
            "type": "Element",
        }
    )
