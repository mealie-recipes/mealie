// CODE_GEN_ID: DATE_LOCALES
import * as afZA from "./lang/dateTimeFormats/af-ZA.json";
import * as arSA from "./lang/dateTimeFormats/ar-SA.json";
import * as bgBG from "./lang/dateTimeFormats/bg-BG.json";
import * as caES from "./lang/dateTimeFormats/ca-ES.json";
import * as csCZ from "./lang/dateTimeFormats/cs-CZ.json";
import * as daDK from "./lang/dateTimeFormats/da-DK.json";
import * as deDE from "./lang/dateTimeFormats/de-DE.json";
import * as elGR from "./lang/dateTimeFormats/el-GR.json";
import * as enGB from "./lang/dateTimeFormats/en-GB.json";
import * as enUS from "./lang/dateTimeFormats/en-US.json";
import * as esES from "./lang/dateTimeFormats/es-ES.json";
import * as etEE from "./lang/dateTimeFormats/et-EE.json";
import * as fiFI from "./lang/dateTimeFormats/fi-FI.json";
import * as frBE from "./lang/dateTimeFormats/fr-BE.json";
import * as frCA from "./lang/dateTimeFormats/fr-CA.json";
import * as frFR from "./lang/dateTimeFormats/fr-FR.json";
import * as glES from "./lang/dateTimeFormats/gl-ES.json";
import * as heIL from "./lang/dateTimeFormats/he-IL.json";
import * as hrHR from "./lang/dateTimeFormats/hr-HR.json";
import * as huHU from "./lang/dateTimeFormats/hu-HU.json";
import * as isIS from "./lang/dateTimeFormats/is-IS.json";
import * as itIT from "./lang/dateTimeFormats/it-IT.json";
import * as jaJP from "./lang/dateTimeFormats/ja-JP.json";
import * as koKR from "./lang/dateTimeFormats/ko-KR.json";
import * as ltLT from "./lang/dateTimeFormats/lt-LT.json";
import * as lvLV from "./lang/dateTimeFormats/lv-LV.json";
import * as nlNL from "./lang/dateTimeFormats/nl-NL.json";
import * as noNO from "./lang/dateTimeFormats/no-NO.json";
import * as plPL from "./lang/dateTimeFormats/pl-PL.json";
import * as ptBR from "./lang/dateTimeFormats/pt-BR.json";
import * as ptPT from "./lang/dateTimeFormats/pt-PT.json";
import * as roRO from "./lang/dateTimeFormats/ro-RO.json";
import * as ruRU from "./lang/dateTimeFormats/ru-RU.json";
import * as skSK from "./lang/dateTimeFormats/sk-SK.json";
import * as slSI from "./lang/dateTimeFormats/sl-SI.json";
import * as srSP from "./lang/dateTimeFormats/sr-SP.json";
import * as svSE from "./lang/dateTimeFormats/sv-SE.json";
import * as trTR from "./lang/dateTimeFormats/tr-TR.json";
import * as ukUA from "./lang/dateTimeFormats/uk-UA.json";
import * as viVN from "./lang/dateTimeFormats/vi-VN.json";
import * as zhCN from "./lang/dateTimeFormats/zh-CN.json";
import * as zhTW from "./lang/dateTimeFormats/zh-TW.json";

const datetimeFormats = {
  "af-ZA": afZA,
  "ar-SA": arSA,
  "bg-BG": bgBG,
  "ca-ES": caES,
  "cs-CZ": csCZ,
  "da-DK": daDK,
  "de-DE": deDE,
  "el-GR": elGR,
  "en-GB": enGB,
  "en-US": enUS,
  "es-ES": esES,
  "et-EE": etEE,
  "fi-FI": fiFI,
  "fr-BE": frBE,
  "fr-CA": frCA,
  "fr-FR": frFR,
  "gl-ES": glES,
  "he-IL": heIL,
  "hr-HR": hrHR,
  "hu-HU": huHU,
  "is-IS": isIS,
  "it-IT": itIT,
  "ja-JP": jaJP,
  "ko-KR": koKR,
  "lt-LT": ltLT,
  "lv-LV": lvLV,
  "nl-NL": nlNL,
  "no-NO": noNO,
  "pl-PL": plPL,
  "pt-BR": ptBR,
  "pt-PT": ptPT,
  "ro-RO": roRO,
  "ru-RU": ruRU,
  "sk-SK": skSK,
  "sl-SI": slSI,
  "sr-SP": srSP,
  "sv-SE": svSE,
  "tr-TR": trTR,
  "uk-UA": ukUA,
  "vi-VN": viVN,
  "zh-CN": zhCN,
  "zh-TW": zhTW,
};
// END: DATE_LOCALES

export default defineI18nConfig(() => {
  return {
    legacy: false,
    locale: "en-US",
    availableLocales: Object.keys(datetimeFormats),
    datetimeFormats: datetimeFormats as any,
    fallbackLocale: "en-US",
    fallbackWarn: true,
  };
});
