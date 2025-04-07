import { OnboardingForm } from '@/components/auth/OnboardingForm';
import { workspaces } from '@/utils/api';

async function getTemplatesAndResources() {
  const [templatesRes, resourcesRes] = await Promise.all([
    workspaces.templates(),
    workspaces.resources(),
  ]);

  return {
    templates: templatesRes.data,
    resources: resourcesRes.data,
  };
}

export default async function OnboardingPage() {
  const { templates, resources } = await getTemplatesAndResources();

  return <OnboardingForm templates={templates} resources={resources} />;
}
