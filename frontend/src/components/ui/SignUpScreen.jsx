import { useCallback, useRef } from 'react';
import { getTranslation } from '@firebase-oss/ui-core';
import {
    Card,
    CardContent,
    CardHeader,
    CardSubtitle,
    CardTitle,
    Divider,
    MultiFactorAuthAssertionScreen,
    Policies,
    RedirectError,
    form as fuiForm,
    useOnUserAuthenticated,
    useRequireDisplayName,
    useSignUpAuthFormAction,
    useSignUpAuthFormSchema,
    useUI,
} from '@firebase-oss/ui-react';

function SignUpScreen({ children, onSignUp, onSignInClick }) {
    const ui = useUI();
    const schema = useSignUpAuthFormSchema();
    const action = useSignUpAuthFormAction();
    const requireDisplayName = useRequireDisplayName();
    const handledUserIdRef = useRef(null);

    const handleSignUp = useCallback(
        (user) => {
            if (handledUserIdRef.current === user.uid) {
                return;
            }

            handledUserIdRef.current = user.uid;
            onSignUp?.(user);
        },
        [onSignUp]
    );

    // Same as SignUpAuthScreen: catches sign ups from child buttons (Google) and MFA
    useOnUserAuthenticated(children || ui.multiFactorResolver ? handleSignUp : undefined);

    const form = fuiForm.useAppForm({
        defaultValues: {
            email: "",
            password: "",
            confirmPassword: "",
            displayName: requireDisplayName ? "" : undefined,
        },
        validators: {
            onChange: schema,
            onSubmitAsync: async ({ value }) => {
                try {
                    const credential = await action(value);
                    if (credential) {
                        handleSignUp(credential.user);
                    }
                } catch (error) {
                    return error instanceof Error ? error.message : String(error);
                }
            },
        },
    });

    if (ui.multiFactorResolver) {
        return <MultiFactorAuthAssertionScreen />;
    }

    return (
        <div className="fui-screen">
            <Card>
                <CardHeader>
                    <CardTitle>{getTranslation(ui, "labels", "signUp")}</CardTitle>
                    <CardSubtitle>{getTranslation(ui, "prompts", "enterDetailsToCreate")}</CardSubtitle>
                </CardHeader>
                <CardContent>
                    <form
                        className="fui-form"
                        onSubmit={async (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            await form.handleSubmit();
                        }}
                    >
                        <form.AppForm>
                            {requireDisplayName ? (
                                <fieldset>
                                    <form.AppField name="displayName">
                                        {(field) => <field.Input label={getTranslation(ui, "labels", "displayName")} />}
                                    </form.AppField>
                                </fieldset>
                            ) : null}
                            <fieldset>
                                <form.AppField name="email">
                                    {(field) => <field.Input label={getTranslation(ui, "labels", "emailAddress")} type="email" />}
                                </form.AppField>
                            </fieldset>
                            <fieldset>
                                <form.AppField
                                    name="password"
                                    validators={{
                                        onChange: ({ value }) =>
                                            value.length < 8
                                                ? { message: "Password must be at least 8 characters" }
                                                : undefined,
                                    }}
                                >
                                    {(field) => <field.Input label={getTranslation(ui, "labels", "password")} type="password" />}
                                </form.AppField>
                            </fieldset>
                            <fieldset>
                                <form.AppField
                                    name="confirmPassword"
                                    validators={{
                                        onChangeListenTo: ["password"],
                                        onChange: ({ value, fieldApi }) =>
                                            value !== fieldApi.form.getFieldValue("password")
                                                ? { message: "Passwords do not match" }
                                                : undefined,
                                    }}
                                >
                                    {(field) => <field.Input label="Confirm Password" type="password" />}
                                </form.AppField>
                            </fieldset>
                            <Policies />
                            <fieldset>
                                <form.SubmitButton>{getTranslation(ui, "labels", "createAccount")}</form.SubmitButton>
                                <form.ErrorMessage />
                            </fieldset>
                            {onSignInClick ? (
                                <form.Action onClick={onSignInClick}>
                                    {getTranslation(ui, "prompts", "haveAccount")} {getTranslation(ui, "labels", "signIn")}
                                </form.Action>
                            ) : null}
                        </form.AppForm>
                    </form>
                    {children ? (
                        <>
                            <Divider>{getTranslation(ui, "messages", "dividerOr")}</Divider>
                            <div className="fui-screen__children">
                                {children}
                                <RedirectError />
                            </div>
                        </>
                    ) : null}
                </CardContent>
            </Card>
        </div>
    );
}

export default SignUpScreen;
