# coding: utf-8

"""
    assets-upload-api

    An autogenerated client for the assets-upload-api.  # noqa: E501

    The version of the OpenAPI document: v1
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from openapi_client.configuration import Configuration


class RobloxOpenCloudAssetsV1AssetType(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    UNSPECIFIED = "Unspecified"
    IMAGE = "Image"
    TSHIRT = "Tshirt"
    AUDIO = "Audio"
    MESH = "Mesh"
    LUA = "Lua"
    HTML = "Html"
    TEXT = "Text"
    HAT = "Hat"
    PLACE = "Place"
    MODEL = "Model"
    SHIRT = "Shirt"
    PANTS = "Pants"
    DECAL = "Decal"
    AVATAR = "Avatar"
    HEAD = "Head"
    FACE = "Face"
    GEAR = "Gear"
    BADGE = "Badge"
    GROUPEMBLEM = "GroupEmblem"
    ANIMATION = "Animation"
    ARMS = "Arms"
    LEGS = "Legs"
    TORSO = "Torso"
    RIGHTARM = "RightArm"
    LEFTARM = "LeftArm"
    LEFTLEG = "LeftLeg"
    RIGHTLEG = "RightLeg"
    PACKAGE = "Package"
    YOUTUBEVIDEO = "YoutubeVideo"
    GAMEPASS = "GamePass"
    APP = "App"
    CODE = "Code"
    PLUGIN = "Plugin"
    SOLIDMODEL = "SolidModel"
    MESHPART = "MeshPart"
    HAIRACCESSORY = "HairAccessory"
    FACEACCESSORY = "FaceAccessory"
    NECKACCESSORY = "NeckAccessory"
    SHOULDERACCESSORY = "ShoulderAccessory"
    FRONTACCESSORY = "FrontAccessory"
    BACKACCESSORY = "BackAccessory"
    WAISTACCESSORY = "WaistAccessory"
    CLIMBANIMATION = "ClimbAnimation"
    DEATHANIMATION = "DeathAnimation"
    FALLANIMATION = "FallAnimation"
    IDLEANIMATION = "IdleAnimation"
    JUMPANIMATION = "JumpAnimation"
    RUNANIMATION = "RunAnimation"
    SWIMANIMATION = "SwimAnimation"
    WALKANIMATION = "WalkAnimation"
    POSEANIMATION = "PoseAnimation"
    LOCALIZATIONTABLEMANIFEST = "LocalizationTableManifest"
    LOCALIZATIONTABLETRANSLATION = "LocalizationTableTranslation"
    EMOTEANIMATION = "EmoteAnimation"
    VIDEO = "Video"
    TEXTUREPACK = "TexturePack"
    TSHIRTACCESSORY = "TshirtAccessory"
    SHIRTACCESSORY = "ShirtAccessory"
    PANTSACCESSORY = "PantsAccessory"
    JACKETACCESSORY = "JacketAccessory"
    SWEATERACCESSORY = "SweaterAccessory"
    SHORTSACCESSORY = "ShortsAccessory"
    LEFTSHOEACCESSORY = "LeftShoeAccessory"
    RIGHTSHOEACCESSORY = "RightShoeAccessory"
    DRESSSKIRTACCESSORY = "DressSkirtAccessory"
    FONTFAMILY = "FontFamily"
    FONTFACE = "FontFace"
    MESHHIDDENSURFACEREMOVAL = "MeshHiddenSurfaceRemoval"
    EYEBROWACCESSORY = "EyebrowAccessory"
    EYELASHACCESSORY = "EyelashAccessory"
    MOODANIMATION = "MoodAnimation"
    DYNAMICHEAD = "DynamicHead"
    CODESNIPPET = "CodeSnippet"

    allowable_values = [UNSPECIFIED, IMAGE, TSHIRT, AUDIO, MESH, LUA, HTML, TEXT, HAT, PLACE, MODEL, SHIRT, PANTS, DECAL, AVATAR, HEAD, FACE, GEAR, BADGE, GROUPEMBLEM, ANIMATION, ARMS, LEGS, TORSO, RIGHTARM, LEFTARM, LEFTLEG, RIGHTLEG, PACKAGE, YOUTUBEVIDEO, GAMEPASS, APP, CODE, PLUGIN, SOLIDMODEL, MESHPART, HAIRACCESSORY, FACEACCESSORY, NECKACCESSORY, SHOULDERACCESSORY, FRONTACCESSORY, BACKACCESSORY, WAISTACCESSORY, CLIMBANIMATION, DEATHANIMATION, FALLANIMATION, IDLEANIMATION, JUMPANIMATION, RUNANIMATION, SWIMANIMATION, WALKANIMATION, POSEANIMATION, LOCALIZATIONTABLEMANIFEST, LOCALIZATIONTABLETRANSLATION, EMOTEANIMATION, VIDEO, TEXTUREPACK, TSHIRTACCESSORY, SHIRTACCESSORY, PANTSACCESSORY, JACKETACCESSORY, SWEATERACCESSORY, SHORTSACCESSORY, LEFTSHOEACCESSORY, RIGHTSHOEACCESSORY, DRESSSKIRTACCESSORY, FONTFAMILY, FONTFACE, MESHHIDDENSURFACEREMOVAL, EYEBROWACCESSORY, EYELASHACCESSORY, MOODANIMATION, DYNAMICHEAD, CODESNIPPET]  # noqa: E501

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
    }

    attribute_map = {
    }

    def __init__(self, local_vars_configuration=None):  # noqa: E501
        """RobloxOpenCloudAssetsV1AssetType - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration
        self.discriminator = None

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, RobloxOpenCloudAssetsV1AssetType):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, RobloxOpenCloudAssetsV1AssetType):
            return True

        return self.to_dict() != other.to_dict()
