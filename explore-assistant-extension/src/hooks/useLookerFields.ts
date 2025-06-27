import { ExtensionContext } from '@looker/extension-sdk-react'
import { useContext, useEffect, useRef } from 'react'
import { useErrorBoundary } from 'react-error-boundary'
import { useDispatch, useSelector } from 'react-redux'
import {
  AssistantState,
  SemanticModel,
  setIsSemanticModelLoaded,
  setSemanticModels,
  setCurrenExplore,
} from '../slices/assistantSlice'
import { RootState } from '../store'

export const useLookerFields = () => {
  const {
    examples: { exploreSamples },
    isSemanticModelLoaded,
    currentExplore,
  } = useSelector((state: RootState) => state.assistant as AssistantState)

  const supportedExplores = Object.keys(exploreSamples)

  const dispatch = useDispatch()
  const { showBoundary } = useErrorBoundary()

  const { core40SDK } = useContext(ExtensionContext)

  // Create a ref to track if the hook has already been called
  const hasFetched = useRef(false)

  // Load LookML metadata and provide completion status
  useEffect(() => {
    // if the hook has already been called, return
    if (hasFetched.current) return

    // if there are no supported explores or the semantic model is already loaded, return
    if (supportedExplores.length === 0 || isSemanticModelLoaded) {
      return
    }

    // mark
    hasFetched.current = true

    const fetchSemanticModel = async (
      modelName: string,
      exploreId: string,
      exploreKey: string,
    ): Promise<SemanticModel | undefined> => {
      if (!modelName || !exploreId) {
        showBoundary({
          message: 'Default Looker Model or Explore is blank or unspecified',
        })
        return
      }

      try {
        const response = await core40SDK.ok(
          core40SDK.lookml_model_explore({
            lookml_model_name: modelName,
            explore_name: exploreId,
            fields: 'fields',
          }),
        )

        const { fields } = response

        if (!fields || !fields.dimensions || !fields.measures) {
          return undefined
        }

        const dimensions = fields.dimensions
          .filter(({ hidden }: any) => !hidden)
          .map(({ name, type, label, description, tags }: any) => ({
            name,
            type,
            label,
            description,
            tags,
          }))

        const measures = fields.measures
          .filter(({ hidden }: any) => !hidden)
          .map(({ name, type, label, description, tags }: any) => ({
            name,
            type,
            label,
            description,
            tags,
          }))

        return {
          exploreId,
          modelName,
          exploreKey,
          dimensions,
          measures,
        }
      } catch (error) {
        console.error(error)
        // showBoundary({
        //   message: `Failed to fetch semantic model for ${modelName}::${exploreId}`,
        // })
        return undefined
      }
    }

    const loadSemanticModels = async () => {
      try {
        const fetchPromises = supportedExplores.map((exploreKey) => {
          const [modelName, exploreId] = exploreKey.split(':')
          return fetchSemanticModel(modelName, exploreId, exploreKey).then(
            (model) => ({ exploreKey, model }),
          )
        })

        const results = await Promise.all(fetchPromises)
        const semanticModels: { [explore: string]: SemanticModel } = {}

        results.forEach(({ exploreKey, model }) => {
          if (model) {
            semanticModels[exploreKey] = model
          }
        })

        dispatch(setSemanticModels(semanticModels))
        dispatch(setIsSemanticModelLoaded(true))
        
        // Update currentExplore to the first available explore from semantic models
        const availableExploreKeys = Object.keys(semanticModels)
        if (availableExploreKeys.length > 0) {
          // Check if current explore is still available
          const currentExploreKey = currentExplore?.exploreKey
          
          // Only update if current explore is not available or not set
          if (!currentExploreKey || !semanticModels[currentExploreKey]) {
            const firstExploreKey = availableExploreKeys[0]
            const firstSemanticModel = semanticModels[firstExploreKey]
            dispatch(setCurrenExplore({
              exploreKey: firstExploreKey,
              modelName: firstSemanticModel.modelName,
              exploreId: firstSemanticModel.exploreId,
            }))
          }
        }
      } catch (error) {
        showBoundary({
          message: 'Failed to load semantic models',
        })
      }
    }

    loadSemanticModels()
  }, [supportedExplores])
}
