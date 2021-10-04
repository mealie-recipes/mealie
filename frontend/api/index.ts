import { RecipeAPI } from "./class-interfaces/recipes";
import { UserApi } from "./class-interfaces/users";
import { GroupAPI } from "./class-interfaces/groups";
import { EventsAPI } from "./class-interfaces/events";
import { BackupAPI } from "./class-interfaces/backups";
import { UploadFile } from "./class-interfaces/upload";
import { CategoriesAPI } from "./class-interfaces/categories";
import { TagsAPI } from "./class-interfaces/tags";
import { UtilsAPI } from "./class-interfaces/utils";
import { NotificationsAPI } from "./class-interfaces/event-notifications";
import { FoodAPI } from "./class-interfaces/recipe-foods";
import { UnitAPI } from "./class-interfaces/recipe-units";
import { CookbookAPI } from "./class-interfaces/group-cookbooks";
import { WebhooksAPI } from "./class-interfaces/group-webhooks";
import { AdminAboutAPI } from "./class-interfaces/admin-about";
import { RegisterAPI } from "./class-interfaces/user-registration";
import { MealPlanAPI } from "./class-interfaces/group-mealplan";
import { EmailAPI } from "./class-interfaces/email";
import { ApiRequestInstance } from "~/types/api";

class AdminAPI {
  private static instance: AdminAPI;
  public about: AdminAboutAPI;

  constructor(requests: ApiRequestInstance) {
    if (AdminAPI.instance instanceof AdminAPI) {
      return AdminAPI.instance;
    }

    this.about = new AdminAboutAPI(requests);

    Object.freeze(this);
    AdminAPI.instance = this;
  }
}

class Api {
  private static instance: Api;
  public recipes: RecipeAPI;
  public users: UserApi;
  public groups: GroupAPI;
  public events: EventsAPI;
  public backups: BackupAPI;
  public categories: CategoriesAPI;
  public tags: TagsAPI;
  public utils: UtilsAPI;
  public notifications: NotificationsAPI;
  public foods: FoodAPI;
  public units: UnitAPI;
  public cookbooks: CookbookAPI;
  public groupWebhooks: WebhooksAPI;
  public register: RegisterAPI;
  public mealplans: MealPlanAPI;
  public email: EmailAPI;

  // Utils
  public upload: UploadFile;

  constructor(requests: ApiRequestInstance) {
    if (Api.instance instanceof Api) {
      return Api.instance;
    }

    // Recipes
    this.recipes = new RecipeAPI(requests);
    this.categories = new CategoriesAPI(requests);
    this.tags = new TagsAPI(requests);
    this.units = new UnitAPI(requests);
    this.foods = new FoodAPI(requests);

    // Users
    this.users = new UserApi(requests);
    this.groups = new GroupAPI(requests);
    this.cookbooks = new CookbookAPI(requests);
    this.groupWebhooks = new WebhooksAPI(requests);
    this.register = new RegisterAPI(requests);
    this.mealplans = new MealPlanAPI(requests);

    // Admin
    this.events = new EventsAPI(requests);
    this.backups = new BackupAPI(requests);
    this.notifications = new NotificationsAPI(requests);

    // Utils
    this.upload = new UploadFile(requests);
    this.utils = new UtilsAPI(requests);

    this.email = new EmailAPI(requests);

    Object.freeze(this);
    Api.instance = this;
  }
}

export { Api, AdminAPI };
