# Shadow of the Tomb Raider Modding Tools

This page will give a quick introduction to the various file types involved, and then explain how to create and package mods.

## File extensions

When modding SOTTR, you'll encounter the following file types:

- **.tiger**

  An archive that contains files and resources. Files have a folder path and filename; resources only have an ID.
  (Previous modding tools have referred to resources as "sections," which is also what the game calls them internally.
  However, this page will refer to them as "resources" for simplicity's sake.)

  If two archives contain the same file, the one with the highest version number in its .nfo takes precedence. This makes it
  possible to mod the game by creating new archives rather than modifying existing ones.

- **.drm**

  The most common file type found in archives. DRM stands for "Data RAM" in this case, not Digital Rights Management.
  These are essentially resource collections: for a certain ingame object such as an outfit piece or weapon,
  they list which resources (meshes, textures...) should be loaded into memory, and in which archives those
  resources can be found.

  It's good to know that .drm files only refer to resources; they don't contain them. Quite often, the same resource
  is referenced by multiple .drm files, which means that modding one texture may affect multiple outfits, for example.
    
- **.tr11objectref**

  The root resource of a .drm resource collection. Contains nothing more than a reference to a .tr11dtp resource (the object
  metadata) which in turn references a skeleton and models.
    
- **.tr11model**

  A small metadata resource that references a model data resource and one or more materials.
    
- **.tr11modeldata**

  Contains mesh geometry, including things like UV maps and blend shapes.
    
- **.tr11material**

  References texture and shader resources, and providers parameters for the latter. Can technically be edited using the binary
  templates, but usually it's easier to simply find an existing material that suits your needs.

- **.dds**

  Regular DirectX texture. The game actually has its own texture format, but it's so close to DDS that the extractor and
  mod manager perform the conversion automatically (without any quality loss).
    
- **.tr11shaderlib**

  Contains one or more compiled shaders (DXBC).
    
- **.tr11contentref**

  The root resource of certain special .drm files containing lists of game content,
  such as collectibles or outfit traits. Just like .tr11objectref, this resource type contains nothing more than a reference
  to a .tr11dtp resource with the actual lists.
        
  .tr11contentref resources can be found in .drm files starting with "global," such as globalcollectibleinfo.drm.

- **.tr11dtp**

  Catch-all resource type used for (almost) everything not listed above.

There are a few other extensions such as .tr11script, which are however unexplored and not moddable.

## Installation

The extractor and manager need no installation and can be run from anywhere. They'll try to autodetect where
SOTTR is installed and ask you to provide the location if they can't find it.

The Blender addon can be installed as follows. Note that it requires Blender **3.6.5** or above (including 4.0).

- Click Edit → Preferences in the menu.
- Select the "Add-ons" tab.
- Click "Install..."
- Select io_scene_sottr.zip.
- Enable the checkmark next to "Import-Export: SOTTR mesh support."

Finally, the binary templates simply need to be placed in the correct folder:

- ImHex: "patterns" subfolder.
- 010 Editor: "010 Templates" subfolder.

## Mesh modding

### Importing

Start by extracting the .drm of the model you want to edit. Then launch Blender, choose File → Import → SOTTR object,
and select the .tr11objectref file. This will import the model's meshes, materials, and skeleton if there is one.

The import filechooser has the following options on the right hand side:

- **Import unlinked models**

  By default, the addon only imports the models referenced by the object metadata. Use this checkbox to instead import all models
  in the "Model" folder.

- **Merge with existing armature(s)**

  In SOTTR, each of Lara's outfits is split into as many as four pieces (head/hair/torso/legs), with each piece having its own skeleton.
  What's more, different skeletons typically have different IDs for the same bone. This of course complicates rigging.

  To solve this problem, the addon can merge the different skeletons into one skeleton that covers the whole outfit.
  Simply import one outfit piece, then import another (and another...) into the same Blender scene with this option
  enabled. The merging feature is explained in more detail later on.

- **Import LODs**

  By default, the addon doesn't import any of the model's LOD meshes to reduce clutter. In certain cases, though,
  you may want to see them: if an original outfit doesn't have a full-detail mesh for one of its parts, or if you're looking
  to replace Lara's head (explained further below).
        
  Note, however, that the addon doesn't support *exporting* LODs. All meshes will be exported as full-detail
  meshes, regardless of whether they were LOD meshes when you imported them. This means you should delete any LOD meshes
  before exporting.

- **Split meshes into parts**

  By default, the addon creates a Blender mesh per SOTTR mesh in the model, where each mesh consists of one or more parts
  (set of polygons sharing the same material). If this isn't granular enough for you, you can enable this option to create
  a Blender mesh per SOTTR mesh part. Alternatively, you can of course use Blender's "Separate By Material" operator
  after importing.

The Blender meshes are named using the following convention:
`<DRM name>_model_<model ID>_<model data ID>_<mesh index>`. Skeletons, bones, materials
etc. follow similar conventions. These names should be left unchanged as they're needed for the export to work.


### Fixing materials

The addon creates a Blender material for every SOTTR material in the "Material" folder (even ones not referenced by the model).
Each Blender material's shader tree contains all the textures used by the SOTTR material, which makes it easier to find
textures to change.

The addon also assigns these materials to the mesh parts, so that you can see a textured preview of the model right after importing.
You'll likely notice, however, that some textures are off. This is because the addon doesn't know which of each material's
textures is the diffuse one — it takes a guess, but it can be wrong. You can fix this by going to Blender's Shading tab and
linking the correct texture yourself.

Note that the Blender shader tree only affects how the material looks in Blender. If you want to change how it looks ingame,
you need to use the binary template instead (or use a different material).

### Normals

The addon imports mesh normals, with an important exception: if a mesh has blend shapes, it lets Blender calculate the normals instead.
The reason is that Blender doesn't support custom vertex normals in blend shapes, only positions.

After importing, it's recommended to use Blender's "Face Orientation" overlay to verify that no faces ended up pointing inside out.
This tends to be the case for the teeth in head meshes for example. Incorrectly oriented faces will appear black ingame.

If you want to remove the custom normals for other meshes (e.g. because they get in the way during editing), you can do so by
selecting the mesh, switching to the Data tab (green triangle) in Blender's Properties panel, expanding the "Geometry Data" header,
and clicking "Clear Custom Split Normals Data."


### Skeletons

SOTTR skeletons contain quite a few bones that aren't used for deforming the model. To reduce clutter, the addon hides
these bones by either moving them to the second bone layer (Blender 3.6) or into a hidden bone collection (Blender 4.0).

When working on outfits, you'll notice something else, too: each outfit is split into multiple pieces — head, hair, torso,
and legs — where each piece has its own .drm file, its own model, and its own skeleton. But the same spine bone
gets a different ID in the torso skeleton than it does in the legs skeleton, and a different ID than the same spine bone
in the torso of another outfit. What's more, the torso and legs of the same outfit can contain bones that have the
same ID despite being different.

The addon comes with a builtin solution for this problem: when you import multiple pieces of an outfit into the same
Blender scene, it'll automatically merge their skeletons into a new skeleton that doesn't have these ID conflicts,
and is compatible across outfits.

The way it works is as follows:

- When you import the first model, you'll notice that each bone in the armature has two IDs in its name.
  The first is the *global ID*, which is referenced by animations and is therefore the same for
  this bone across all pieces of all outfits. The second is the *local ID*, which is referenced
  by the weights of the model but is different in each outfit piece.

- When you import a second model with the "Merge with existing armature(s)" option enabled,
  the addon will create a new armature containing the bones of both the first and second skeleton
  (duplicates removed), and all the bones renamed to use *just* the global ID. It also parents the
  meshes of both the first and second model to this new armature and renames their vertex groups to match.

  The original armatures are moved to a hidden collection named "Split meshes for export" and should
  not be deleted.

- If needed, import the third and fourth pieces of the outfit as well. (Note that exporting heads with
  blend shapes is slow, so it's generally recommended to import those without merging so you can
  export them separately later on.)

- You can now edit the meshes — or delete them and start from scratch — and weight them for the single, merged skeleton.
- When you do an export, the addon will automatically create copies of the meshes (inside the hidden collection),
  rename their vertex groups to match the original piece-specific skeletons, and export those copies.

  If a mesh spans multiple skeletons, the addon will automatically split it up. This tends to result in
  visible seams ingame, however, so it's better to split the meshes yourself in a place where the seams are
  minimized or hidden.

It's important to note that, while all bones in an outfit piece have a local ID, not all of them have a global ID.
This applies to the physics bones in an outfit-specific loose strip of fabric, for example.
Such bones have an "x" in place of a global ID in their name, and are not included in the merged skeleton —
which means you also can't weight meshes for them there.

If you have such a situation, you can do the following:

- Create a base version of the outfit based on the merged skeleton (where physics bones are not available).
- Export it to create the split meshes in the hidden collection.
- Delete the merged skeleton and meshes from the scene, and bring the split skeletons and meshes
  out of the hidden collection. You can also delete the Empty objects parented to the split skeletons.
- Finish the outfit based on the split skeletons (where all bones are available) and export again.

### Mesh editing

Previous modding tools have resorted to patching/amending the original file, which limited the changes you could make.
This toolset, however, exports model files from scratch, which gives you a lot more freedom. Specifically, you can:

- Add, change, and remove meshes as you please. (There's no need to keep the mesh index at the end of the
  object name sequential.)
- Add, change, and remove blend shapes as you please.
- Add, change, and remove material slots as you please, and freely assign different materials to faces.
  You can also reference materials that weren't originally referenced by the model — *including* materials from
  another .drm file. It's enough to rename the Blender material to use the ID of the external SOTTR material,
  but you can of course also import the external .drm file into the current scene and delete its armature/meshes again,
  keeping just the materials.


### Head modding

If you're looking to replace Lara's head by a custom one, you'll run into two problems: blend shapes and PureHair.

The head mesh has over a hundred blend shapes for facial expressions, used in cutscenes and the Photo Mode. Replicating all these
on a custom mesh would be quite the undertaking. Fortunately, it's not necessary: SOTTR also supports bone-based facial animation,
meaning all you really have to do is transfer the weights. The full-detail head mesh isn't weighted for facial bones,
but the LOD meshes are, which is where the "Import LODs" option comes in handy.

Lara's hair, in turn, is stored in a PureHair file that's referenced by the object metadata. You can't remove it through
mesh editing — instead, you need to use the binary templates. This is done as follows:

- Open the head's .tr11objectref in one of the supported hex editors.
- Apply the "tr11objectref" template.
  - ImHex: File → Import → Pattern File
  - 010 Editor: Templates → Open Template... followed by Templates → Run Template
- Find the `objectRef` entry and note its number.
- Open the .tr11dtp file corresponding to this number and apply the "tr11object" template.
- Find the `simpleComponents` entry, and within it, the `DYNAMICHAIR` entry.
- Change the `type` field of the hair entry to `_NONE`.
- Save the file and include it in your mod.

### Exporting

Exporting is done through the menu item File → Export → SOTTR model. The addon will export
the models you have selected, or all models in the scene if none are selected. It'll produce both a .tr11model file and
a .tr11modeldata file per model.

As mentioned before, the addon creates model files from scratch, so there's no need to overwrite an existing file.

The addon will automatically add a Triangulate modifier to meshes that don't have one yet, and temporarily disable
all other modifiers so they don't affect the export result.

## Animation modding

Apart from models, the Blender addon also supports importing and exporting animations (.tr11anim files).
You can animate bone positions/rotations/scales and blendshape values.

To find an animation to modify, you can use a binary template to browse the .tr11animlib files in e.g. tr11_lara.drm.
These files map animation names to IDs, where the IDs correspond to the names of the .tr11anim files.

You can also check the appendix at the end of this page to find the IDs of the photo mode poses.

Once you've found an animation you'd like to edit or replace, you'll want to do the following:

- Import tr11_lara.tr11objectref from tr11_lara.drm and delete the dummy model, keeping just the skeleton.
- Import the head, torso, and leg models of some outfit.
- Import the .tr11anim file (File → Import → SOTTR animation).
- Edit the animation. While imported animations have a keyframe on every frame, this is not required for
  custom animations.
- Export the animation to a .tr11anim file (File → Export → SOTTR animation). As with models, there's no
  need to overwrite an existing file.

The addon supports bone constraints. In fact, it automatically creates constraints on a few (hidden by default)
bones of the tr11_lara skeleton, as this is necessary for the animation to play correctly ingame.

The animation's duration is determined by the Blender scene's end frame, and its speed by the FPS Base.

## External references

Most SOTTR resources reference other resources. A .tr11objectref references an object. An object references
a skeleton and models. A model references materials, which in turn reference textures and shaders, and so on.

You can change a model's material references by simply applying different materials in Blender. However,
by using the binary templates, you can edit other references as well. For example, you could make an
object point to a different skeleton.

When changing such an external reference, you can make it point to any resource in the game,
*even if that resource is not included in the DRM*. The mod manager will automatically
add the referenced resource (and any resources it references in turn) to the DRM so that the game
won't crash.

This also means you can simply overwrite a resource by a copy of any other resource. For example,
you could overwrite a material by another and change just one texture reference, keeping the
shader references and the other textures. 

## Mod packaging

Creating mods for installation with the manager is quite simple: just throw the modified resource files in a
folder or compressed archive (.zip/.7z/.rar) and you're done. There's no need to include any .drm files
(in fact, these aren't extracted in the first place).

> [!TIP]
> When testing your mod during development, it's easiest to drag-and-drop the folder straight onto the
> mod manager window to install it. Packing the mod into an archive is only necessary when you're ready
> to publish it.
> 
> What's more: if you install from a folder, the manager will first automatically uninstall
> the existing mod with the same name (if present) so that you don't have to do this manually,
> saving you some time when iterating.

For textures, simply use DDS files; the manager will automatically convert them back to the game-specific texture
format during installation (again without loss of quality). However, you should make sure to generate mipmaps,
and ideally use the same compression as the original textures.

You can organize your files in subfolders in any way you like: by file type, by model they belong to... or not at all.

Note that a resource may be referenced by multiple .drm resource collections. Modding a texture that you extracted
for just one outfit may well end up affecting other outfits too.


### Variations

The mod manager supports mods with variations, such as differently colored versions of the same outfit.
This is again quite simple to set up:

- Create a subfolder for each variation.
- Within each subfolder, create one or both of the following files:
  - variation.txt: a plaintext file containing a description of the variation.
  - variation.png: a preview image.
- Place the variation-specific resource files in their respective subfolder (either as direct
  children or inside deeper subfolders).
- Place the resource files that are common to all variations in the root of the mod or in
  a subfolder that's not (part of) a variation.

When installing a mod with variations, the manager will present users with a window where they
can choose the one they like.

> [!TIP]
> This window is also shown if the mod contains only one variation, which can be useful
> if you have no variations but still want to present users with e.g. a readme before installing.

## Appendix 1: Outfit reference

| Ingame name | Name in globalcollectibleinfo.drm | Model .drm prefix |
| ----------- | ---------------------------------- | ------------------ |
| Adventurer | Lara_Prologue | paperdoll_piece_tr11_lara_jungle |
| Angel Of Darkness | Lara_Loyalty_AOD | paperdoll_piece_tr11_lara_aod |
| Blue Henley | Lara_Loyalty_TR10_BlueHenley | paperdoll_piece_tr11_lara_tr10_blue_henley |
| Blue Heron Tunic | Lara_Outsider | paperdoll_piece_tr11_lara_outsider |
| Bomber Jacket | Lara_Loyalty_TR2BomberJacket | paperdoll_piece_tr11_lara_tr2_bomber |
| Boots Of The Empress Jaguar | Stealth_01_Legs | paperdoll_piece_tr11_lara_stealth_01_legs |
| Brocken | HighTech_01 | paperdoll_piece_tr11_lara_dlc_hightech |
| Brocken - Shadow | DLC_Outfit_01 | paperdoll_piece_tr11_lara_dlc_hightech_alt |
| Ch'Amaka's Greaves | Assault_03_Legs | paperdoll_piece_tr11_lara_assault_03_legs |
| Ch'Amaka's War Vest  | Assault_03_Torso | paperdoll_piece_tr11_lara_assault_03_torso |
| Commando | Lara_Loyalty_TR10_Commando | paperdoll_piece_tr11_lara_tr10_commando |
| Condor Cowl Of Urqu | Stealth_02_Torso | paperdoll_piece_tr11_lara_stealth_02_torso |
| Crimson Huntress | Lara_CrimsonHuntress | paperdoll_piece_tr11_lara_priest |
| Croft Fitness | DLC_Outfit_13 | paperdoll_piece_tr11_lara_workout_nostraps |
| Desert Tank | Lara_Loyalty_TR10_DesertTank | paperdoll_piece_tr11_lara_tr10_desert_tanktop |
| Dragon Scales | Kukulkan_01 | paperdoll_piece_tr11_lara_dlc_kukulkan_alt |
| Dragon Scales - Legend | DLC_Outfit_05 | paperdoll_piece_tr11_lara_dlc_kukulkan |
| Eveningstar's Boots | Exploration_01_Legs | paperdoll_piece_tr11_lara_exploration_01_legs |
| Eveningstar's Cape | Exploration_01_Torso | paperdoll_piece_tr11_lara_exploration_01_torso |
| Explorer | Lara_Explorer | paperdoll_piece_tr11_lara_explorer |
| Gray Henley | Lara_Loyalty_TR10_GrayHenley | paperdoll_piece_tr11_lara_tr10_gray_henley |
| Greaves Of Six Sky | Assault_02_Legs | paperdoll_piece_tr11_lara_assault_02_legs |
| Hide Boots Of Urqu | Stealth_02_Legs | paperdoll_piece_tr11_lara_stealth_02_legs |
| Hunter's Array | Trinity_01 | paperdoll_piece_tr11_lara_trinity |
| Hunter's Array - Apex | DLC_Outfit_04 | paperdoll_piece_tr11_lara_trinity_alt |
| Infiltrator | Lara_Loyalty_TR10_Infiltrator | paperdoll_piece_tr11_lara_tr10_infiltrator |
| Kantu's Boots | Exploration_03_Legs | paperdoll_piece_tr11_lara_exploration_03_legs |
| Kantu's Gilded Vest | Exploration_03_Torso | paperdoll_piece_tr11_lara_exploration_03_torso |
| Leather Jacket | Lara_Loyalty_TR10_LeatherJacket | paperdoll_piece_tr11_lara_tr10_london_jacket |
| Manko's Boots | Stealth_03_Legs | paperdoll_piece_tr11_lara_stealth_03_legs |
| Manko's Tunic | Stealth_03_Torso | paperdoll_piece_tr11_lara_stealth_03_torso |
| Mantle Of Six Sky | Assault_02_Torso | paperdoll_piece_tr11_lara_assault_02_torso |
| Midnight Sentinel | DLC_Outfit_11 | paperdoll_piece_tr11_lara_dlc_original_yaaxil |
| Midnight Sentinel - Farseer | DLC_Outfit_07 | paperdoll_piece_tr11_lara_dlc_original_yaaxil_alt |
| Nine Strides' Boots | Exploration_02_Legs | paperdoll_piece_tr11_lara_exploration_02_legs |
| Nine Strides' Harness | Exploration_02_Torso | paperdoll_piece_tr11_lara_exploration_02_torso |
| Ozcollo's Greaves | Jaguar_01_Legs | paperdoll_piece_tr11_lara_path_jaguar_legs |
| Ozcollo's Tunic | Jaguar_01_Torso | paperdoll_piece_tr11_lara_path_jaguar_torso |
| Quenti Palla's Greaves | Eagle_01_Legs | paperdoll_piece_tr11_lara_path_eagle_legs |
| Quenti Palla's Mantle | Eagle_01_Torso | paperdoll_piece_tr11_lara_path_eagle_torso |
| Remnant Jacket | Lara_Loyalty_TR10_RemnantJacket | paperdoll_piece_tr11_lara_tr10_remnant |
| Reptile Hide | Predator_01 | paperdoll_piece_tr11_lara_dlc_predator |
| Reptile Hide - Leviathan | DLC_Outfit_06 | paperdoll_piece_tr11_lara_dlc_predator_alt |
| Robes Of Puka Huk | Lara_Shaman | paperdoll_piece_tr11_lara_crimson_huntress |
| Scales Of Q | Yaaxil_01 | paperdoll_piece_tr11_lara_yaaxil |
| Scales Of Q - Feathered Serpent | DLC_Outfit_03 | paperdoll_piece_tr11_lara_yaaxil_alt |
| Serpent Guard | Lara_WarriorPriest | paperdoll_piece_tr11_lara_highpriest |
| Shadow Runner | Lara_Loyalty_TR10_ShadowRunner | paperdoll_piece_tr11_lara_tr10_shadowrunner_torso |
| Siberian Ranger | Lara_Loyalty_TR10_SiberianRanger | paperdoll_piece_tr11_lara_tr10_siberian_ranger |
| Sinchi Chiqa Battle Dress | Rebel_01 | paperdoll_piece_tr11_lara_dlc_rebelwarrior |
| Sinchi Chiqa Battle Dress - Honor Guard | DLC_Outfit_02 | paperdoll_piece_tr11_lara_dlc_rebelwarrior_alt |
| Survivor | Lara_Loyalty_TR9_ShipwreckedSurvivor | paperdoll_piece_tr11_lara_tr9_yamatai |
| Tactical Adventurer | Lara_BlueTank | paperdoll_piece_tr11_lara_tactical |
| Tactical Adventurer (Black) | Lara_Classic | paperdoll_piece_tr11_lara_classic |
| Tactical Adventurer Classic | DLC_Outfit_12 | paperdoll_piece_tr11_lara_tactical_alt |
| Three Fangs' Greaves | Snake_01_Legs | paperdoll_piece_tr11_lara_path_snek_legs |
| Three Fangs' Tunic | Snake_01_Torso | paperdoll_piece_tr11_lara_path_snek_torso |
| Tomb Raider 2 | Lara_Loyalty_TR2 | paperdoll_piece_tr11_lara_tr2 |
| Tunic Of The Exiled Fox | Huntress_01 | paperdoll_piece_tr11_lara_dlc_huntress |
| Tunic Of The Shorn One | DLC_Outfit_10 | paperdoll_piece_tr11_lara_quoriankasuit |
| Vest Of The Empress Jaguar | Stealth_01_Torso | paperdoll_piece_tr11_lara_stealth_01_torso |
| Wraithskin | Lara_Loyalty_TR10_Wraithskin | paperdoll_piece_tr11_lara_tr10_wraithskin |
| Yaway's Battle Tunic | Assault_01_Torso | paperdoll_piece_tr11_lara_assault_01_torso |
| Yaway's Wooden Greaves | Assault_01_Legs | paperdoll_piece_tr11_lara_assault_01_legs |
| (Main menu) |  | paperdoll_generator_lara_menu |

## Appendix 2: Photo mode reference

The .tr11anim files listed below can be found in tr11_lara.drm.

### Face

| Ingame name | .tr11anim ID |
| ----------- | ------------ |
| Neutral | 30901 |
| Smiling | 30900 |
| Happy | 30899 |
| Sly | 30898 |
| Sad | 30897 |
| Surprised | 30896 |
| Disgusted | 30895 |
| Angry | 30894 |
| Wonderment | 30893 |
| Displeased | 30892 |
| Smug | 33016 |
| Annoyed | 33018 |
| Innocent | 33017 |

### Body

| Ingame name | .tr11anim ID |
| ----------- | ------------ |
| Celebrating | 33015 |
| Exulting | 33014 |
| Victorious | 33013 |
| Flexing | 33006 |
| Framing High | 33005 |
| Framing Eye Level | 32998 |
| Thumbs Up | 33003 |
| Scouting | 33012 |
| Sneaking | 33001 |
| Kneeling | 32999 |
| Folded | 33011 |
| Balancing Left | 33004 |
| Balancing Right | 33007 |
| Predatory | 32997 |
| Successful | 33010 |
