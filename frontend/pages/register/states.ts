import { reactive } from "@nuxtjs/composition-api";

export enum States {
  Initial,
  ProvideToken,
  ProvideGroupDetails,
  ProvideCredentials,
  ProvideAccountDetails,
  SelectGroupOptions,
  Confirmation,
}

export enum RegistrationType {
  Unknown,
  JoinGroup,
  CreateGroup,
  InitialGroup,
}

interface Context {
  state: States;
  type: RegistrationType;
}

interface RegistrationContext {
  ctx: Context;
  setState(state: States): void;
  setType(type: RegistrationType): void;
  back(): void;
}

export function useRegistration(): RegistrationContext {
  const context = reactive({
    state: States.Initial,
    type: RegistrationType.Unknown,
    history: [
      {
        state: States.Initial,
      },
    ],
  });

  function saveHistory() {
    context.history.push({
      state: context.state,
    });
  }

  const back = () => {
    const last = context.history.pop();
    if (last) {
      context.state = last.state;
    }
  };

  const setState = (state: States) => {
    saveHistory();
    context.state = state;
  };

  const setType = (t: RegistrationType) => {
    context.type = t;
  };

  return { ctx: context, setType, setState, back };
}
